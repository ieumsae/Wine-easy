from flask import Flask, request, jsonify
from db.db import get_wine_info_by_name
from flask import Blueprint

app = Flask(__name__)

wineasyTEXT = Blueprint('wineasyTEXT', __name__)

@wineasyTEXT.route('/process_text', methods=['POST'])
def process_text():
    try:
        print("Request received")  # 요청이 도달했는지 확인

        data = request.get_json()
        if data is None:
            return jsonify({"error": "No data received"}), 400
        print(f"Received data: {data}")  # 요청 데이터를 로그에 출력

        # JSON 데이터에서 wine_name 추출
        action = data.get('action', {})
        params = action.get('params', {})
        wine_name = params.get('wine_name', None)

        if not wine_name:
            detail_params = action.get('detailParams', {})
            wine_name = detail_params.get('wine_name', {}).get('value', None)

        # 만약 wine_name이 여전히 없다면 userRequest의 utterance 사용
        if not wine_name:
            wine_name = data.get('userRequest', {}).get('utterance', None)

        if not wine_name:
            return jsonify({"error": "wine_name 파라미터가 필요합니다."}), 400

        print(f"wine_name: {wine_name}")  # 추출된 값을 로그에 출력

        # 와인 데이터 가져오기
        try:
            wine_details = get_wine_info_by_name(wine_name)
        except Exception as e:
            print(f"Error fetching wine details: {e}")
            return jsonify({"error": "Error fetching wine details"}), 500
            
        print(f"Retrieved wine details: {wine_details}")

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
                f"{wine_emoji} {wine['wine_name_ko']} {wine_emoji}\n"
                f"({wine['wine_name_en']})\n\n"
                "📝 테이스팅 노트\n\n"
                f"\"{wine['taste']}\"\n\n"
                "🍽 페어링하기 좋은 음식\n\n"
                f"{numbered_food_list}\n\n"
                "추천이 도움이 되셨을까요?\n"
                "페어링 추천이 필요한\n"
                f"{wine_emoji}다른 와인{wine_emoji}이 있으시다면\n"
                "👇 하단 메뉴에서 👇\n"
                "'처음으로'를 눌러주세요 😆"
            )
        else:
            skill_text = (
                "죄송해요...\n"
                "저희가 찾아드릴 수 있는\n" 
                "와인이 아닌가봐요 😥\n\n"

                "페어링을 찾고 싶은\n" 
                "🍷다른 와인🍷이 있으시다면\n"
                "👇 하단 메뉴에서 👇\n"
                "'처음으로'를 눌러주세요 😆"
            )
        skill_data = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": skill_text
                        }
                    }
                ]
            }
        }
        return jsonify(skill_data)
    except Exception as e:
        print(f"Error processing request: {e}")  # 예외 발생 시 에러 로그 출력
        return jsonify({"error": str(e)}), 500  # 500 응답 반환

if __name__ == '__main__':
    app.run(port=5000, debug=True)  # Flask 서버 실행
