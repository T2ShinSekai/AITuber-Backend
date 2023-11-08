import os, openai, json
import settings
from youtube import YoutubeLive
from schema import Message
from dotenv import load_dotenv
import requests

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
news_api_key = os.getenv("NEWS_API_KEY")
openai.api_key = api_key


class PromptTemplate:
    def __init__(self, input_variables, template):
        self.input_variables = input_variables
        self.template = template

    def generate_buffer(self, variable_values):
        if not all(key in variable_values for key in self.input_variables):
            raise ValueError("Not all input variables provided values")

        return self.template.format(**variable_values)


MAX_HISTORY_LENGTH = 500

class Agent:

    def __init__(self):
        self.message_history = []
        self.buffer_messages = {"messages": []}
        self.youtube = YoutubeLive()
        self.last_seen_message_ids = set()
        self.count = 0

    def new_topic(self, genre: str):
        # News APIのエンドポイントURL
        base_url = "https://newsapi.org/v2/top-headlines"

        headers = {'X-Api-Key': news_api_key}
        # パラメーターの設定
        params = {
            "country": "jp",  # 国を指定 (例: "de" for Germany)
            "category": genre,  # ジャンルを指定
            "pageSize": 1       # 1件のニュースを取得
        }

        try:
            # ニュースのリクエストを送信
            response = requests.get(base_url, headers=headers, params=params)

            # レスポンスのJSONデータを取得
            data = response.json()

            # ニュース記事が存在する場合、概要を取得
            if data["articles"]:
                top_news = data["articles"][0]
                title = top_news["title"]
                description = top_news["description"]
                return f"タイトル: {title}\n概要: {description}"
            else:
                return "指定されたジャンルのニュースが見つかりませんでした。"

        except Exception as e:
            return f"エラーが発生しました: {str(e)}"

    def get_live_chat(self):
        messages = self.youtube.get_live_chat_messages()
        if messages == None:
            return

        new_messages = [msg for msg in messages if msg['id'] not in self.last_seen_message_ids]

        for message in new_messages:
            print(message['snippet']['displayMessage'])
            self.last_seen_message_ids.add(message['id'])
            user_name = message['authorDetails']['displayName']
            user_message = message['snippet']['displayMessage']
            self.buffer_messages["messages"].append({
                "name": user_name,
                "message": user_message
            })
        # pass


    def set_new_messages(self, name, message):
        self.buffer_messages["messages"].append({
            "name": name,
            "message": message
        })

    def get_new_messages(self):
        new_messages = self.buffer_messages
        self.buffer_messages = {"messages": []}
        return new_messages


    def buffer_memory(self):

        _BUFFER_MEMORY_TEMPLATE_ = """
            Character: {character}
            Agenda: {agenda}
            Command: {command}
            Example: {example}
            Format: {format}
        """

        buffer = PromptTemplate(
            input_variables=["character", "agenda", "command", "example"],
            template=_BUFFER_MEMORY_TEMPLATE_,
        )

        # 記憶の復元
        character = settings.AGENT_CHARACTER
        agenda = settings.AGETN_AGENDA
        command = settings.AGENT_COMMAND
        format = settings.AGETN_FORMAT
        example = settings.AGETN_EXAMPLE

        input_variables = {
            "character": character,
            "agenda": agenda,
            "command": command,
            "format": format,
            "example": example,
        }

        memory = buffer.generate_buffer(input_variables)
        return memory


    def execute(self, new_message: Message):
        self.messages = []

        buffer_memory = self.buffer_memory()
        self.messages.append({"role": "system", "content": buffer_memory})

        # 履歴のappend
        self.messages.extend(self.message_history[-10:])

        # メモリ対策
        if len(self.message_history) >= MAX_HISTORY_LENGTH:
            del self.message_history[0:len(self.message_history) - MAX_HISTORY_LENGTH + 1]

        self.messages.append({"role": "user", "content": new_message.message})
        self.message_history.append({"role": "user", "content": new_message.message})

        print("messages: ", self.messages)

        functions = [
            {
                "name": "new_topic",
                "description": "新しいニュースの概要を提供する関数です。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "genre": {
                            "type": "string",
                            "description": "one of these - business,entertainment,general,health,science,sports,technology",
                        },
                    },
                },
            },
        ]

        gpt_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=self.messages,
            functions=functions,
            function_call="auto",
        )
        response_message = gpt_response["choices"][0]["message"]
        if response_message.get("function_call"):
            available_functions = {
                "new_topic": self.new_topic,
            }
            function_name = response_message["function_call"]["name"]
            if function_name == "new_topic":
                function_to_call = available_functions[function_name]
                function_args = json.loads(response_message["function_call"]["arguments"])
                function_response = function_to_call(
                    genre = function_args.get("genre"),
                )
            self.messages.append(
                    {
                        "role": "function",
                        "name": function_name,
                        "content": function_response,
                    }
                )
            gpt_response_with_function_call = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0613",
                messages=self.messages,
            )
            result_with_fc = gpt_response_with_function_call["choices"][0]["message"]["content"]
            self.message_history.append({"role": "assistant", "content": result_with_fc})
            return result_with_fc
        else:
            result_without_cd = gpt_response["choices"][0]["message"]["content"]
            self.message_history.append({"role": "assistant", "content": result_without_cd})
            return result_without_cd






