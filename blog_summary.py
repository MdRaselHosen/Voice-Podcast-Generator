import os
from dotenv import load_dotenv
from crewai import LLM, Agent, Crew, Process, Task
from crewai_tools import FirecrawlScrapeWebsiteTool
from elevenlabs.client import ElevenLabs

load_dotenv()

# ---------------------------------------------------------
# 1. Initialize LLM & Tools
# ---------------------------------------------------------
llm = LLM(
    model="openrouter/meta-llama/llama-3.1-8b-instruct",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

firecrawl_tool = FirecrawlScrapeWebsiteTool(
    api_key=os.getenv("FIRECRAWL_API_KEY")
)

blog_scraper = Agent(
    name="Blog Scraper",
    role="Web Content Scraper",
    goal="Extract and return the full markdown text from a webpage using the provided tool.",
    backstory=(
        "You are an automated scraping worker. Your primary job is to execute "
        "the tool to fetch full website content and return raw text cleanly."
    ),
    llm=llm,
    tools=[firecrawl_tool],
    verbose=True,
    allow_delegation=False,
)

blog_summarizer = Agent(
    name="Blog Summarizer",
    role="Podcast Script Writer",
    goal="Transform scraped text context directly into a 100-200 word summary.",
    backstory=(
        "You are an automated pipeline agent. You NEVER ask the user for input or state "
        "that content is missing. You strictly take the provided context output from the "
        "scraping task and turn it into a clear, engaging podcast summary script."
    ),
    llm=llm,
    verbose=True,
    allow_delegation=False,
)


def scrape_blog_task(url):
    return Task(
        description=(
            f"Use the FirecrawlScrapeWebsiteTool to scrape all main text from {url}. "
            "Do not guess the content. Call the tool and return the output."
        ),
        expected_output="Full scraped text content in markdown format.",
        agent=blog_scraper,
    )

def summarize_blog_task(scraped_task_ref):
    return Task(
        description=(
            "Review the scraped text context from the previous task. "
            "Summarize the main points into a smooth, conversational podcast script segment. "
            "Do not include any URLs, headers, or conversational filler like 'Here is your summary'."
        ),
        expected_output="A clean 100-200 word podcast-ready summary text.",
        agent=blog_summarizer,
        context=[scraped_task_ref]
    )


def create_blog_summary_crew(url):
    scrape_task = scrape_blog_task(url)
    summarize_task = summarize_blog_task(scrape_task)

    crew = Crew(
        agents=[blog_scraper, blog_summarizer],
        tasks=[scrape_task, summarize_task],
        verbose=True,
        process=Process.sequential,
    )

    return crew

def summarize_blog(url):
    crew = create_blog_summary_crew(url)
    result = crew.kickoff()
    return str(result.raw)


def generate_voiceover(text, output_filename="summary_podcast.mp3"):
    print("\n--- Generating Audio with ElevenLabs ---")
    client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
    
    audio = client.generate(
        text=text,
        voice="Rachel",
        model="eleven_multilingual_v2"
    )
    
    with open(output_filename, "wb") as f:
        for chunk in audio:
            f.write(chunk)
            
    print(f"Audio successfully saved to {output_filename}")


if __name__ == "__main__":
    target_url = "https://mdraselhosen.github.io/Portfolio/"
    
    summary_text = summarize_blog(target_url)
    print("\n=== Generated Summary Script ===")
    print(summary_text)
    
    if summary_text and not summary_text.isspace():
        generate_voiceover(summary_text, "portfolio_summary.mp3")