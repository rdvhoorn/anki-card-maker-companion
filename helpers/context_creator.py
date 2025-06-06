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

        self.word_base_form_agent = Agent(
            'openai:gpt-4o-mini',
            system_prompt="""
You are a word base form assistant. You will be given a Spanish word, and you will return the base form of that word.
If the word is plural, return the base form of the singular form of the word. If the word can be both masculine and feminine, return both, separated by a slash.
So, given "compañeros", you will return "compañero / compañera".
Return only the base form, no other text.
"""
        )

        self.article_agent = Agent(
            'openai:gpt-4o-mini',
            system_prompt="""
You are an article assistant. You will be given a Spanish word, and you will return the article that should be used with that word.
Return only the article(s), no other text.
"""
        )

    def create_clue(self, word):
        return self.clue_finetuning_agent.run_sync(word).output
    
    def get_context(self, word):
        return self.article_agent.run_sync(word).output, self.ipa_spelling_agent.run_sync(word).output

    def get_word_base_form(self, word):
        return self.word_base_form_agent.run_sync(word).output
