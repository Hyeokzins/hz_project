from pynput.mouse import Listener  # 마우스 이벤트를 모니터링하기 위한 라이브러리
import tkinter as tk  # GUI를 생성하기 위한 라이브러리
from PIL import ImageGrab , Image  # 화면 캡처를 위한 라이브러리
import easyocr  # 이미지에서 텍스트를 인식하는 라이브러리
import threading  # 멀티스레딩을 위한 라이브러리
import time  # 시간 지연을 위한 라이브러리
import cv2 as cv  # OpenCV 라이브러리
import numpy as np  # 배열 연산을 위한 라이브러리
import requests  # HTTP 요청을 보내기 위한 라이브러리
import os
import win32gui, win32api
from tkinter import messagebox
os.environ['KMP_DUPLICATE_LIB_OK']='True'


'''소스코드에 사용될 변수를 메모장에서 가져오기 (url , 디폴트 캡처 좌표) '''
variables = []

with open('variable.txt', 'r') as memo_file:
    lines = memo_file.readlines()

for line in lines: 
    #line = 한줄
    if '=' in line:
        # '='을 기준으로 문자열을 분리하고 좌우 공백을 제거하고 '=' 다음 단어를 저장
        parts = line.split('=')
        variable_value = parts[1].strip()
        variables.append(variable_value)
        
#변수 배당
url, Default_x, Default_y, Default_width, Default_height = variables[:5]


'''캡처 구역 사각형 시각화'''
class Draw:
    def __init__(self):
        hwnd = win32gui.GetDesktopWindow()
        self.hdc = win32gui.GetDC(hwnd)
        
    def rect(self, left_top, right_bottom):
        # 빨간색으로 고정 (RGB 값: 255, 0, 0)
        color = win32api.RGB(255, 0, 0)
        # 좌상단과 우하단 좌표
        x1, y1 = left_top
        x2, y2 = right_bottom
        # 주어진 좌표로 사각형을 그립니다.
        for i in range(x1, x2 + 1):
            win32gui.SetPixel(self.hdc, i, y1, color) # 상단
            win32gui.SetPixel(self.hdc, i, y2, color) # 하단
        for j in range(y1, y2 + 1):
            win32gui.SetPixel(self.hdc, x1, j, color) # 왼쪽
            win32gui.SetPixel(self.hdc, x2, j, color) # 오른쪽

def draw_rectangle():
    while True:
        try:
            x1, y1 = min(start_x, end_x), min(start_y, end_y)  
            x2, y2 = max(start_x, end_x), max(start_y, end_y)  
            app = Draw()
            app.rect((x1, y1), (x2, y2))
            time.sleep(0.1)  
        except TypeError:
            time.sleep(0.1)
            continue  
        # 캡처 좌표가 없는 상태에서도 이 함수는 종료되서는 안됨


recognized_result = ""  # 이미지 인식 결과를 저장할 변수

# 화면 캡처를 위한 변수들 초기화
start_x, start_y = None, None
end_x, end_y = None, None
capture_done = False

def on_click(x, y, button, pressed):
    """마우스 이벤트 처리 콜백 함수"""
    global start_x, start_y, end_x, end_y, capture_done

    if pressed:  # 마우스 버튼이 눌러졌을 때
        start_x, start_y = x, y  # 캡처 시작 좌표 저장
    else:  # 마우스 버튼이 떼어졌을 때
        end_x, end_y = x, y  # 캡처 종료 좌표 저장
        capture_done = True  # 캡처 완료 플래그 설정
        # Stop listener (마우스 이벤트 리스너 종료)
        return False

def capture_screen():
    """화면 캡처를 수행하는 함수"""
    with Listener(on_click=on_click) as listener:  # 마우스 이벤트 리스너 생성
        listener.join()  # 리스너 실행

def save_capture_result():
    """화면 캡처 영역에서 텍스트를 인식하고 결과를 저장하는 함수"""
    while True:
        global capture_done
        try:
            x1, y1 = min(start_x, end_x), min(start_y, end_y)  # 캡처 영역 좌상단 좌표 
            x2, y2 = max(start_x, end_x), max(start_y, end_y)  # 캡처 영역 우하단 좌표
        except TypeError: 
            print('좌표 입력을 대기중입니다') 
            break  # 해당 반복문을 빠져나옵니다.
        app = Draw()
        app.rect((x1, y1), (x2, y2))
        # 화면 캡처 수행
        screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        
        if (x2 - x1) < 41 or (y2 - y1) < 13:
            # 캡처 영역이 작을 경우 이미지를 10배 확대
            screenshot = screenshot.resize((screenshot.width * 20, screenshot.height * 15), Image.LANCZOS)
            print('이미지가 확대 되었습니다')   
        img_frame = np.array(screenshot)
        img_frame = cv.cvtColor(img_frame, cv.COLOR_RGB2BGR)
        
        # 이미지에서 텍스트 인식
        reader = easyocr.Reader(['en'])
        result = reader.readtext(img_frame, detail=0)
        print('텍스트 인식결과',result)  # 결과 출력

        global recognized_result
        recognized_result = result  # 인식 결과 저장

        data = {'text': recognized_result}
        response = requests.post(url, data=data)
        print(f"Server response: {response.text}")
        
        root.update()
        
        ##캡처 완료 여부 
        capture_done = False  # 캡처 완료 플래그 초기화
        
def set_coordinates():
    '''좌표 수동입력'''
    global start_x, start_y, end_x, end_y
    x = int(x_entry.get())  # x 좌표 입력받기
    y = int(y_entry.get())  # y 좌표 입력받기
    width = int(width_entry.get())  # 폭 입력받기
    height = int(height_entry.get())  # 높이 입력받기
    start_x, start_y = x, y
    end_x, end_y = x + width, y + height
    tk.messagebox.showinfo("알림", f"캡처 영역이 설정되었습니다: ({start_x}, {start_y}) - ({end_x}, {end_y})")
    save_capture_result()

def capture_and_save():
    """화면 캡처 및 텍스트 인식 작업을 수행하는 함수"""
    global capture_done

    if not capture_done:  # 캡처가 완료되지 않았을 경우에만 수행
        print("마우스로 원하는 영역을 드래그하세요.")
        capture_screen()  # 화면 캡처 시작
        print(f"캡처 영역: ({start_x}, {start_y}) - ({end_x}, {end_y})")
        save_capture_result()  # 캡처 영역에서 텍스트 인식 및 결과 저장
        
def stop_capture_area():
    '''캡처구역 초기화 함수'''
    global start_x, start_y, end_x, end_y, capture_done
    start_x, start_y = None, None
    end_x, end_y = None, None
    capture_done = False
    tk.messagebox.showinfo("알림", "캡처 영역이 초기화 되었습니다 다시 캡처하기 버튼을 눌러 영역을 지정하세요.")

def exit_program():
    '''gui종료 프로그램 종료시 영업종료를 알리는 키워드를 서버로 전송'''
    global exit_flag
    exit_flag = True  # 종료 플래그 설정
    data = {'text':'exit'}
    response = requests.post(url, data=data)
    print(f"Server response: {response.text}")
    root.destroy()  # Tkinter 애플리케이션 종료
    os._exit(0)     # 모든 스레드 종료 및 프로세스 종료


'''프로그램 작동 시작 부분'''
if __name__ == "__main__":
    exit_flag = False  # 종료 플래그 초기화

    rectangle_thread = threading.Thread(target=draw_rectangle)
    rectangle_thread.daemon = True
    rectangle_thread.start()  # 사각형 그리기 스레드 시작
    
    capture_thread = threading.Thread(target=save_capture_result)
    capture_thread.daemon = True
    capture_thread.start()  # 캡처 및 텍스트 인식 스레드 시작

    root = tk.Tk()  # Tkinter 애플리케이션 생성
    root.title("화면 캡처")
    root.geometry("300x250")  # 창 크기 설정
    
    #수동설정 라벨
    label_manual = tk.Label(root, text="수동설정 (단위:px)")
    label_manual.grid(row=0, column=0,columnspan=2)
    
    # 드래그설정 라벨
    label_drag = tk.Label(root, text="드래그 설정") 
    label_drag.grid(row=0, column=2, columnspan=2)
    
    # x좌표
    label_x = tk.Label(root, text="x 좌표") 
    label_x.grid(row=1, column=0)
    x_entry = tk.Entry(root,width=5)
    x_entry.grid(row=1, column=1)
    x_entry.insert(0, Default_x)
    
    #드래그로 캡처구역 설정하는 버튼
    capture_button = tk.Button(root, text="드래그 캡처", command=capture_and_save)
    capture_button.grid(row=1, column=2 ,columnspan=2)  # 캡처 버튼 생성 및 GUI에 추가
    
    # y좌표
    label_y = tk.Label(root, text="y 좌표") 
    label_y.grid(row=2, column=0) 
    y_entry = tk.Entry(root,width=5)
    y_entry.grid(row=2, column=1)
    y_entry.insert(0, Default_y)
    
    # 너비
    label_width = tk.Label(root, text="너비") 
    label_width.grid(row=3, column=0)
    width_entry = tk.Entry(root,width=5)
    width_entry.grid(row=3, column=1)
    width_entry.insert(0, Default_width)
    
    # 높이
    label_height = tk.Label(root, text="높이") 
    label_height.grid(row=4, column=0)
    height_entry = tk.Entry(root,width=5)
    height_entry.grid(row=4, column=1)
    height_entry.insert(0, Default_height)
    
    # 좌표 설정 캡처 버튼
    set_coordinates_button = tk.Button(root, text="좌표 캡처", command=set_coordinates)
    set_coordinates_button.grid(row=5, column=0 ,columnspan=2)  # 설정 버튼 생성 및 GUI에 추가
    
    # 부가 기능 라벨
    label_extra = tk.Label(root, text="부가 기능") 
    label_extra.grid(row=3, column=2, columnspan=2)
    
    #캡처 구역 초기화
    reset_button = tk.Button(root, text="캡처 구역 초기화", command=stop_capture_area)
    reset_button.grid(row=4, column=2 ,columnspan=2) # 캡처 구역 초기화 버튼 
    
    #종료 버튼
    exit_button = tk.Button(root, text="종료", command=exit_program)
    exit_button.grid(row=5, column=2 ,columnspan=2)  # 종료 버튼 생성 및 GUI에 
    
    '''gui 비율 맞추기'''
    for i in range(6): 
        root.grid_rowconfigure(i, weight=1) 
        root.grid_columnconfigure(i, weight=1)

    root.mainloop()  # Tkinter 애플리케이션 실행