from pydantic_ai import Agent

class ContextCreator:

    def __init__(self):
        self.clue_finetuning_agent = Agent(
            'openai:gpt-4o-mini',
            system_prompt="""
You are a clue creator assistant.
Given a word, check if that word is a Spanish verb conjugation. If it is, return the verb infinitive. If it is not, return nothing.
Return only the verb infinitive, or nothing at all. 
        """
        )

        self.ipa_spelling_agent = Agent(
            'openai:gpt-4o-mini',
            system_prompt="""
You are an IPA spelling assistant. You will be given a European spanish word, and you will return the IPA transcription of that word.
Return only the IPA transcription, no other text.
            """
        )

    def create_clue(self, word):
        return self.clue_finetuning_agent.run_sync(word).output
    
    def get_context(self, word):
        return "el", self.ipa_spelling_agent.run_sync(word).output
