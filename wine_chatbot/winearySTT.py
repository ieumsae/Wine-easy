import streamlit as st  
import speech_recognition as sr  
from gtts import gTTS  
import playsound  
import os  
from db.db import get_wine_info_by_name 
from wineasyTEXT import process_text  
import re

# 음성 파일 경로 설정 및 초기화
file_path="E:/workplace/wineasy/wineasy_1.2.1/kakao_skill/ttsFole.mp3"
if os.path.exists(file_path):
    os.remove(file_path)  # 기존 음성 파일이 있으면 삭제
fileName=file_path

# 텍스트를 음성으로 변환하고 재생하는 함수
def SpeakText(text):
    text_without_emojis = remove_emojis(text)
    SaveMp3File(text_without_emojis)  # 텍스트를 음성 파일로 저장
    playsound.playsound(fileName)  # 음성 파일 재생
    print("대답 내용 : " + text_without_emojis)  # 디버깅용으로 출력

# 텍스트를 MP3 파일로 저장하는 함수
def SaveMp3File(text):
    tts = gTTS(text=text, lang='ko')  # 텍스트를 한국어 음성으로 변환
    tts.save(fileName)  # 파일로 저장

def remove_emojis(text):
    # 이모티콘만 제거하는 정규 표현식
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # 이모티콘
        "\U0001F300-\U0001F5FF"  # 기호 및 그림문자
        "\U0001F680-\U0001F6FF"  # 교통 및 지도 기호
        "\U0001F1E0-\U0001F1FF"  # 깃발 (iOS)
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

# 메인 함수 - Streamlit 앱 실행
def main():
    st.title("음성으로 페어링 찾기")  # 웹 페이지 제목 설정

    # 음성 인식 시작 버튼
    if st.button("음성 인식 시작"):
        # 음성 인식 객체 생성
        read = sr.Recognizer()

        with sr.Microphone() as source:
            st.write("와인 이름을 말씀해 주세요...")  # 사용자에게 음성 입력을 요청
            audio = read.listen(source)  # 마이크로부터 음성을 입력받음

        try:
            # Google Speech Recognition을 사용하여 음성을 텍스트로 변환
            text = read.recognize_google(audio, language="ko-KR")
            st.write("인식된 텍스트:", text)  # 인식된 텍스트를 화면에 출력

            # 와인 정보를 데이터베이스에서 가져오기
            wine_details = get_wine_info_by_name(text)
            
            # 결과 출력
            if wine_details:
                wine = wine_details[0]
                wine_type = wine['wine_type']

                # 와인 타입에 따른 이모지 선택
                wine_emoji = {
                    "레드": "🍷",
                    "화이트": "🥂",
                    "스파클링": "🍾"
                }.get(wine_type, "🍷")  # 기본값은 레드 와인 이모지

                numbered_food_list = '\n'.join([f"{i+1}. {food.strip()}" for i, food in enumerate(wine['recommended_dish'].split(','))])

                skill_text = (
                    f"{wine_emoji} {wine['wine_name_ko']} {wine_emoji}\n\n"
                    f"({wine['wine_name_en']})\n\n"
                    
                    "📝 테이스팅 노트\n\n"

                    f"\"{wine['taste']}\"\n\n"

                    "🍽 페어링하기 좋은 음식\n\n"

                    f"{numbered_food_list}\n\n"

                    "추천이 도움이 되셨을까요?\n\n"
                    f"페어링 추천이 필요한 {wine_emoji}다른 와인{wine_emoji}이 있으시다면\n\n"
                    "상단의 '음성인식 시작'을 눌러주시거나\n\n" 
                    "챗봇으로 다시 돌아가서 '라벨로 페어링 찾기'\n\n"
                    "혹은 '문자열로 페어링 찾기' 기능을 이용해주세요 😆"
                )
                skill_text2 = (
                    f"검색된 와인은 {wine['wine_name_ko']} 입니다."
                )
                st.subheader("검색된 와인은")
                st.subheader(f"{wine['wine_name_ko']}")
                st.subheader(f"({wine['wine_name_en']})입니다.")
                st.write(skill_text)
                SpeakText(skill_text2)  # 음성으로 출력
            else:
                skill_text = (
                    "죄송해요...\n\n"
                    "저희가 찾아드릴 수 있는 와인이 아닌가봐요 😥\n\n" 

                    "페어링을 찾고 싶은 🍷다른 와인🍷이 있으시다면\n\n" 
                    "상단의 '음성인식 시작'을 눌러주시거나\n\n" 
                    "챗봇으로 다시 돌아가서 '라벨로 페어링 찾기'\n\n"
                    "혹은 '문자열로 페어링 찾기' 기능을 이용해주세요 😆"
                )
                skill_text2 = (
                    "죄송해요...저희가 찾아드릴 수 있는 와인이 아닌가봐요"
                )
                st.write(skill_text)
                SpeakText(skill_text2)
        except sr.UnknownValueError:
            st.write("음성을 인식할 수 없습니다.")  # 음성을 인식하지 못했을 때 예외 처리
        except sr.RequestError as e:
            st.write(f"음성 인식 서비스 오류: {e}")  # 음성 인식 서비스에 문제가 있을 때 예외 처리
        except Exception as e:
            print(e)  # 기타 예외를 출력
        
# 이 스크립트가 메인으로 실행될 때, main() 함수를 호출
if __name__ == "__main__":
    main()