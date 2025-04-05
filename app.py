from flask import Flask, render_template, request, jsonify
import random
import json
import os

app = Flask(__name__)

# 랜덤 질문과 답변 옵션
QUESTIONS = [
    {
        "question": "오늘 입은 옷의 색은?",
        "options": ["흰색", "검정색", "파란색", "빨간색", "노란색", "초록색", "회색", "분홍색"]
    },
    {
        "question": "좋아하는 계절은?",
        "options": ["봄", "여름", "가을", "겨울"]
    },
    {
        "question": "가장 최근에 본 영화의 장르는?",
        "options": ["액션", "로맨스", "코미디", "공포", "SF", "애니메이션", "드라마"]
    },
    {
        "question": "오늘 아침에 먹은 음식은?",
        "options": ["밥", "빵", "샐러드", "과일", "시리얼", "안 먹음", "기타"]
    },
    {
        "question": "지금 신고 있는 신발 종류는?",
        "options": ["운동화", "구두", "샌들", "슬리퍼", "부츠", "맨발"]
    },
    {
        "question": "가장 좋아하는 음료는?",
        "options": ["커피", "차", "주스", "탄산음료", "물", "술"]
    }
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_question', methods=['POST'])
def get_question():
    data = request.get_json()
    participants = data.get('participants', [])
    
    # 랜덤 질문 선택
    question_data = random.choice(QUESTIONS)
    
    return jsonify({
        'question': question_data['question'],
        'options': question_data['options']
    })

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    total_amount = data.get('totalAmount', 0)
    participants = data.get('participants', [])
    answers = data.get('answers', {})
    
    # 행운의 답변 선택
    options = list(answers.values())
    if not options:
        return jsonify({'error': 'No answers provided'}), 400
        
    lucky_answer = random.choice(options)
    
    # 각 답변 별 선택한 사람 수 확인
    answer_counts = {}
    for answer in options:
        if answer not in answer_counts:
            answer_counts[answer] = 0
        answer_counts[answer] += 1
    
    # 행운의 답변을 선택한 사람들
    lucky_participants = [p for p in participants if answers.get(p) == lucky_answer]
    
    # 기본 1/N 금액
    base_amount = total_amount / len(participants)
    
    # 결과 계산
    result = {}
    
    # 행운의 답변을 선택한 경우 추가 금액 설정 (2000원 고정)
    extra_amount = 2000
    
    if lucky_participants:
        # 행운의 답변 선택자 수
        lucky_count = len(lucky_participants)
        # 그 외 참가자 수
        unlucky_count = len(participants) - lucky_count
        
        if unlucky_count > 0:
            # 행운의 답변을 선택한 사람들이 더 내는 총 금액
            total_extra = extra_amount * unlucky_count
            # 1인당 추가 금액
            extra_per_lucky = total_extra / lucky_count
            # 할인 금액
            discount_per_unlucky = total_extra / unlucky_count
            
            # 금액 계산
            for p in participants:
                if p in lucky_participants:
                    # 행운의 답변을 선택한 참가자는 추가 금액
                    result[p] = round(base_amount + extra_per_lucky, -3)  # 1000원 단위로 반올림
                else:
                    # 행운이 없는 참가자는 할인
                    result[p] = round(base_amount - discount_per_unlucky, -3)  # 1000원 단위로 반올림
        else:
            # 모든 참가자가 행운의 답변을 선택한 경우
            for p in participants:
                result[p] = round(base_amount, -3)  # 1000원 단위로 반올림
    else:
        # 행운의 답변을 선택한 사람이 없는 경우 (이론적으로는 발생하지 않음)
        for p in participants:
            result[p] = round(base_amount, -3)  # 1000원 단위로 반올림
    
    # 반올림으로 인한 총액 차이 확인 및 조정
    total_after_rounding = sum(result.values())
    difference = total_amount - total_after_rounding
    
    # 차이가 있으면 무작위 참가자에게 할당하여 총액 맞추기
    if difference != 0:
        random_participant = random.choice(participants)
        result[random_participant] += difference
    
    # 최종 금액이 너무 작으면 100원 단위로 조정
    for p in participants:
        if result[p] < 1000:
            result[p] = round(result[p], -2)  # 100원 단위로 반올림
    
    return jsonify({
        'luckyAnswer': lucky_answer,
        'result': result
    })

if __name__ == '__main__':
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # HTML 파일 생성
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write('''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>행운의 더치페이</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background: #076324;
            color: #fff;
            text-align: center;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: rgba(0, 0, 0, 0.5);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        }
        h1 {
            color: #FFD700;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
            font-size: 2rem;
        }
        h2 {
            font-size: 1.5rem;
        }
        .step {
            margin-bottom: 30px;
        }
        input, button {
            padding: 10px;
            margin: 5px;
            border-radius: 5px;
            border: none;
            font-size: 16px;
            max-width: 100%;
        }
        button {
            background: #FFD700;
            color: #000;
            cursor: pointer;
            transition: all 0.3s;
        }
        button:hover {
            background: #FFC107;
            transform: scale(1.05);
        }
        .card-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 10px;
            margin-top: 20px;
        }
        .card {
            width: 110px;
            height: 150px;
            background: #fff;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #000;
            font-weight: bold;
            cursor: pointer;
            perspective: 1000px;
            transition: transform 0.3s;
            position: relative;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            padding: 5px;
            text-align: center;
            word-break: keep-all;
        }
        .card:hover {
            transform: translateY(-5px);
        }
        .card.selected {
            border: 3px solid #FFD700;
        }
        .card.shuffling {
            animation: shuffle 1s ease-in-out;
        }
        .card.lucky {
            background: #FFD700;
            animation: pulse 1.5s infinite;
        }
        .participant-badges {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 8px;
            margin: 10px 0;
        }
        .participant-badge {
            display: inline-block;
            background: #333;
            padding: 5px 10px;
            border-radius: 15px;
            cursor: pointer;
        }
        .participant-badge.active {
            background: #FFD700;
            color: #000;
        }
        .result-card {
            background: rgba(255, 255, 255, 0.9);
            color: #000;
            padding: 15px;
            border-radius: 8px;
            margin: 10px;
            text-align: left;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        .result-amount {
            font-size: 1.2em;
            font-weight: bold;
            color: #e74c3c;
        }
        .lucky-participant {
            color: #D4AF37;
            font-weight: bold;
        }
        .unlucky-participant {
            color: #3498db;
        }
        @keyframes shuffle {
            0% { transform: translateX(0) rotate(0); }
            25% { transform: translateX(50px) rotate(5deg); }
            50% { transform: translateX(-50px) rotate(-5deg); }
            75% { transform: translateX(25px) rotate(2deg); }
            100% { transform: translateX(0) rotate(0); }
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        #shuffleAnimation {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 100;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s;
        }
        #shuffleAnimation.active {
            opacity: 1;
            pointer-events: all;
        }
        .card-back {
            background: linear-gradient(135deg, #e74c3c 25%, #3498db 25%, #3498db 50%, #e74c3c 50%, #e74c3c 75%, #3498db 75%);
            background-size: 20px 20px;
            width: 80px;
            height: 120px;
            border-radius: 5px;
            position: absolute;
            backface-visibility: hidden;
        }
        #currentParticipantDisplay {
            font-size: 1.2rem;
            font-weight: bold;
            background: rgba(0, 0, 0, 0.3);
            padding: 10px;
            border-radius: 5px;
            display: inline-block;
            margin: 10px 0;
        }
        #questionDisplay {
            font-size: 1.2rem;
            margin: 15px 0;
            background: rgba(0, 0, 0, 0.3);
            padding: 10px;
            border-radius: 5px;
        }
        .results-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 10px;
        }
        
        /* 반응형 스타일 */
        @media (max-width: 768px) {
            .container {
                padding: 15px;
                margin: 0 10px;
            }
            h1 {
                font-size: 1.8rem;
            }
            h2 {
                font-size: 1.3rem;
            }
            .card {
                width: 90px;
                height: 120px;
                font-size: 0.9rem;
            }
            input, button {
                width: 90%;
                margin: 5px auto;
                display: block;
            }
            .participant-badge {
                padding: 5px 8px;
                font-size: 0.9rem;
            }
            #questionDisplay {
                font-size: 1.1rem;
            }
        }
        
        @media (max-width: 480px) {
            h1 {
                font-size: 1.5rem;
            }
            h2 {
                font-size: 1.2rem;
            }
            .card {
                width: 80px;
                height: 110px;
                font-size: 0.8rem;
            }
            .result-card {
                padding: 10px;
                margin: 5px;
            }
            #questionDisplay {
                font-size: 1rem;
                padding: 8px;
            }
            .participant-badge {
                padding: 4px 6px;
                font-size: 0.8rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🍀 행운의 더치페이 🍀</h1>
        
        <div id="step1" class="step">
            <h2>Step 1: 식사 금액 입력</h2>
            <input type="number" id="totalAmount" placeholder="식사 비용 (원)" min="1000" step="100">
            <button onclick="goToStep2()">다음</button>
        </div>
        
        <div id="step2" class="step" style="display: none;">
            <h2>Step 2: 인원 설정</h2>
            <input type="number" id="numParticipants" placeholder="인원 수" min="2" max="20">
            <button onclick="setupParticipants()">다음</button>
        </div>
        
        <div id="step3" class="step" style="display: none;">
            <h2>Step 3: 참가자 이름 입력</h2>
            <div id="participantInputs"></div>
            <button onclick="startGame()">게임 시작</button>
        </div>
        
        <div id="step4" class="step" style="display: none;">
            <h2>Step 4: 질문에 답해주세요</h2>
            <div id="questionDisplay"></div>
            <div id="currentParticipantDisplay"></div>
            <div id="participantSelectors" class="participant-badges"></div>
            <div id="optionsContainer" class="card-container"></div>
            <button id="finishAnswering" disabled onclick="finishAnswering()">결과 보기</button>
        </div>
        
        <div id="step5" class="step" style="display: none;">
            <h2>Step 5: 행운의 결과</h2>
            <div id="luckyAnswerDisplay"></div>
            <div id="resultsContainer" class="results-container"></div>
            <button onclick="resetGame()">다시 하기</button>
        </div>
    </div>
    
    <div id="shuffleAnimation">
        <div class="card-container" id="shuffleCards"></div>
    </div>
    
    <script>
        let totalAmount = 0;
        let participants = [];
        let currentQuestion = "";
        let options = [];
        let answers = {};
        let currentParticipantIndex = 0;
        
        function goToStep2() {
            const amountInput = document.getElementById('totalAmount');
            totalAmount = parseInt(amountInput.value);
            
            if (!totalAmount || totalAmount < 1000) {
                alert('유효한 식사 비용을 입력해주세요 (최소 1,000원)');
                return;
            }
            
            document.getElementById('step1').style.display = 'none';
            document.getElementById('step2').style.display = 'block';
        }
        
        function setupParticipants() {
            const numInput = document.getElementById('numParticipants');
            const num = parseInt(numInput.value);
            
            if (!num || num < 2 || num > 20) {
                alert('유효한 인원 수를 입력해주세요 (2-20명)');
                return;
            }
            
            const container = document.getElementById('participantInputs');
            container.innerHTML = '';
            
            for (let i = 1; i <= num; i++) {
                const input = document.createElement('input');
                input.type = 'text';
                input.id = `participant${i}`;
                input.placeholder = `참가자 ${i} 닉네임`;
                input.required = true;
                container.appendChild(input);
                container.appendChild(document.createElement('br'));
            }
            
            document.getElementById('step2').style.display = 'none';
            document.getElementById('step3').style.display = 'block';
        }
        
        function startGame() {
            participants = [];
            const inputs = document.querySelectorAll('#participantInputs input');
            
            let allFilled = true;
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    allFilled = false;
                } else {
                    participants.push(input.value.trim());
                }
            });
            
            if (!allFilled) {
                alert('모든 참가자의 닉네임을 입력해주세요');
                return;
            }
            
            // 중복 닉네임 검사
            const uniqueNames = new Set(participants);
            if (uniqueNames.size !== participants.length) {
                alert('중복된 닉네임이 있습니다. 모두 다른 닉네임을 사용해주세요.');
                return;
            }
            
            // 질문 가져오기
            fetch('/get_question', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ participants }),
            })
            .then(response => response.json())
            .then(data => {
                currentQuestion = data.question;
                options = data.options;
                
                document.getElementById('questionDisplay').textContent = currentQuestion;
                
                // 참가자 선택기 생성
                const selectorsContainer = document.getElementById('participantSelectors');
                selectorsContainer.innerHTML = '';
                
                participants.forEach((p, index) => {
                    const badge = document.createElement('div');
                    badge.className = 'participant-badge';
                    badge.textContent = p;
                    badge.dataset.index = index;
                    selectorsContainer.appendChild(badge);
                });
                
                // 옵션 카드 생성
                const optionsContainer = document.getElementById('optionsContainer');
                optionsContainer.innerHTML = '';
                
                options.forEach(option => {
                    const card = document.createElement('div');
                    card.className = 'card';
                    card.textContent = option;
                    card.onclick = () => selectOption(option);
                    optionsContainer.appendChild(card);
                });
                
                answers = {};
                currentParticipantIndex = 0;
                document.getElementById('step3').style.display = 'none';
                document.getElementById('step4').style.display = 'block';
                
                // 첫 번째 참가자 선택 상태로 설정
                updateCurrentParticipant();
            });
        }
        
        function updateCurrentParticipant() {
            const currentParticipant = participants[currentParticipantIndex];
            document.getElementById('currentParticipantDisplay').textContent = `현재 차례: ${currentParticipant}`;
            
            // 참가자 뱃지 업데이트
            document.querySelectorAll('.participant-badge').forEach(badge => {
                badge.classList.remove('active');
                if (parseInt(badge.dataset.index) === currentParticipantIndex) {
                    badge.classList.add('active');
                }
            });
            
            // 이미 응답한 경우 해당 카드 표시
            document.querySelectorAll('.card').forEach(card => {
                card.classList.remove('selected');
                if (answers[currentParticipant] === card.textContent) {
                    card.classList.add('selected');
                }
            });
        }
        
        function selectOption(option) {
            const currentParticipant = participants[currentParticipantIndex];
            
            // 응답 저장
            answers[currentParticipant] = option;
            
            // UI 업데이트
            document.querySelectorAll('.card').forEach(card => {
                card.classList.remove('selected');
                if (card.textContent === option) {
                    card.classList.add('selected');
                }
            });
            
            // 다음 참가자로 이동
            currentParticipantIndex++;
            if (currentParticipantIndex >= participants.length) {
                // 모든 참가자가 답변을 마침
                document.getElementById('finishAnswering').disabled = false;
                // 마지막 참가자가 응답한 후에도 해당 참가자를 표시
                currentParticipantIndex = participants.length - 1;
            }
            
            updateCurrentParticipant();
        }
        
        function shuffleAnimation() {
            return new Promise((resolve) => {
                const shuffleElement = document.getElementById('shuffleAnimation');
                const cardsContainer = document.getElementById('shuffleCards');
                
                // 카드 생성
                cardsContainer.innerHTML = '';
                options.forEach(option => {
                    const card = document.createElement('div');
                    card.className = 'card';
                    card.innerHTML = `<div class="card-back"></div>`;
                    cardsContainer.appendChild(card);
                    
                    // 무작위 위치에 배치
                    card.style.position = 'absolute';
                    card.style.left = `${Math.random() * 60 + 20}%`;
                    card.style.top = `${Math.random() * 60 + 20}%`;
                    card.style.transform = `rotate(${Math.random() * 360}deg)`;
                });
                
                // 애니메이션 표시
                shuffleElement.classList.add('active');
                
                // 카드 셔플 애니메이션
                const cards = cardsContainer.querySelectorAll('.card');
                let intervalIds = [];
                
                cards.forEach(card => {
                    card.classList.add('shuffling');
                    
                    // 무작위 이동 애니메이션
                    const intervalId = setInterval(() => {
                        card.style.left = `${Math.random() * 60 + 20}%`;
                        card.style.top = `${Math.random() * 60 + 20}%`;
                        card.style.transform = `rotate(${Math.random() * 360}deg)`;
                    }, 500);
                    
                    intervalIds.push(intervalId);
                });
                
                // 3초 후 애니메이션 종료
                setTimeout(() => {
                    // 모든 인터벌 제거
                    intervalIds.forEach(id => clearInterval(id));
                    shuffleElement.classList.remove('active');
                    resolve();
                }, 3000);
            });
        }
        
        function finishAnswering() {
            // 셔플 애니메이션 실행
            shuffleAnimation().then(() => {
                // 결과 계산
                fetch('/calculate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        totalAmount,
                        participants,
                        answers
                    }),
                })
                .then(response => response.json())
                .then(data => {
                    const luckyAnswer = data.luckyAnswer;
                    const result = data.result;
                    
                    // 결과 표시
                    document.getElementById('luckyAnswerDisplay').innerHTML = 
                        `<h3>🎉 오늘의 행운의 답은 <span class="lucky-participant">${luckyAnswer}</span> 입니다! 🎉</h3>`;
                    
                    const resultsContainer = document.getElementById('resultsContainer');
                    resultsContainer.innerHTML = '';
                    
                    participants.forEach(p => {
                        const isLucky = answers[p] === luckyAnswer;
                        
                        const card = document.createElement('div');
                        card.className = 'result-card';
                        card.innerHTML = `
                            <h3>${p}</h3>
                            <p>답변: ${answers[p]}</p>
                            <p class="result-amount">${result[p].toLocaleString()}원</p>
                            <p>${isLucky ? 
                                '<span class="lucky-participant">🎊 축하합니다! 오늘은 당신이 쏩니다!</span>' : 
                                '<span class="unlucky-participant">🍀 다음에 더 행운이 있을 거예요!</span>'}</p>
                        `;
                        
                        resultsContainer.appendChild(card);
                    });
                    
                    document.getElementById('step4').style.display = 'none';
                    document.getElementById('step5').style.display = 'block';
                });
            });
        }
        
        function resetGame() {
            document.getElementById('step5').style.display = 'none';
            document.getElementById('step1').style.display = 'block';
            document.getElementById('totalAmount').value = '';
            document.getElementById('numParticipants').value = '';
        }
    </script>
</body>
</html>
        ''')
    
    app.run(host='0.0.0.0', port=6644, debug=True)
