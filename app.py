#!/usr/bin/env python3
"""
AI News Analyst - Web UI
Simple Gradio interface for the AI News Analyst application
"""

import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import gradio as gr
from src.workflow.news_analysis_workflow import run_news_analysis

def analyze_question(question):
    """
    Process user question and return AI response
    """
    if not question or not question.strip():
        return "Please enter a question."
    
    try:
        result = run_news_analysis(question.strip())
        return result
    except Exception as e:
        return f"Error: {str(e)}\n\nPlease check your API key and try again."

# Create the Gradio interface
with gr.Blocks(title="AI News Analyst", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # AI News Analyst
        
        Ask me anything about **recent news** or **Wiki**!
        
        - For current events and tech news, I'll search my news database
        - For general knowledge, I'll consult Wikipedia
        """
    )
    
    with gr.Row():
        with gr.Column():
            question_input = gr.Textbox(
                label="Your Question",
                placeholder="E.g., What are the latest developments in AI? or Who was Albert Einstein?",
                lines=3
            )
            
            with gr.Row():
                submit_btn = gr.Button("Analyze", variant="primary", scale=2)
                clear_btn = gr.Button("Clear", scale=1)
    
    response_output = gr.Textbox(
        label="AI Response",
        lines=15,
        show_copy_button=True
    )
    

    
    # Event handlers
    submit_btn.click(
        fn=analyze_question,
        inputs=question_input,
        outputs=response_output
    )
    
    question_input.submit(
        fn=analyze_question,
        inputs=question_input,
        outputs=response_output
    )
    
    clear_btn.click(
        fn=lambda: ("", ""),
        inputs=None,
        outputs=[question_input, response_output]
    )
    
   
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )

