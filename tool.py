import requests
import base64

def get_user_input():
    username = input("账号: ")
    password = input("密码: ")
    return username, password

def encode_password(password):
    password_bytes = password.encode('utf-8')
    base64_encoded = base64.b64encode(password_bytes).decode('utf-8')
    return '3' + base64_encoded

def get_token(username, pwd):
    headers = {
        "authorization": "Basic d2ViOnFsdGVhY2hlcg==",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    }

    data = {
        "username": username,
        "password": pwd,
        "grant_type": "password",
        "pws": "b"
    }

    url = "https://id.qlteacher.com/api/auth/token"
    response = requests.post(url, headers=headers, data=data)

    if response.status_code != 200:
        print("登录失败，请检查密码")
        exit()
        
    data = response.json()
    token = data["access_token"]
    return token

def get_course_ids(token):
    headers = {
        "Authorization": f"Bearer {token}",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    }

    response = requests.get("https://yanxiu.qlteacher.com/api/project/xx2023/user/me", headers=headers)

    if response.status_code == 200:
        data = response.json()
        courses = data["lessonList"]
        course_ids = [course["courseId"] for course in courses]
        return course_ids
    else:
        print("课程获取失败")
        exit()

def get_video_ids(course_ids, token):
    base_url = 'https://yanxiu.qlteacher.com/api/project/xx2023/learning/'
    video_ids = []

    headers = {
        "Authorization": f"Bearer {token}",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    }

    for course_id in course_ids:
        url = base_url + course_id
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            video_url = data.get("data")
            if video_url:
                video_id = video_url.split("/")[-1]
                video_ids.append(video_id)
        else:
            print("一级课程ID获取失败")
            exit()

    return video_ids

def update_video_duration(video, activity, act_token, token):
    headers = {
        "Authorization": f"Bearer {token}",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    }

    url = f"https://player.qlteacher.com/api/learning/{video}/duration/video/{activity}/{act_token}/-1?_ignore_error=true"
    data = "{}"  
    response = requests.put(url, headers=headers, data=data)

    if response.status_code == 200:
        print("刷课成功")

def main():
    username, password = get_user_input()
    pwd = encode_password(password)
    token = get_token(username, pwd)
    course_ids = get_course_ids(token)
    video_ids = get_video_ids(course_ids, token)



    headers = {
        "Authorization": f"Bearer {token}",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    }


    for video in video_ids:
        print("当前刷课的一级课程ID：", video)
        url = f"https://player.qlteacher.com/api/learning/{video}/course"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            activitys = data["data"]["sections"][0]["activitys"]
            activity_ids = [activity["id"] for activity in activitys]
            print("成功取得二级课程ID，开始刷课")
            
            for activity in activity_ids:
                print("当前刷课的二级课程ID：", activity)
                url = f"https://player.qlteacher.com/api/learning/{video}/activity/{activity}"
                response = requests.get(url, headers=headers)
                if response.status_code != 200:
                    print("获取actToken失败")
                    exit()

                data = response.json()
                act_token = str(data["data"]["actToken"])
                length = data["data"]["activity"]["standard"]
                times = length / 60
                offset = 0

                while times > 1:
                    offset += 60
                    url = f"https://player.qlteacher.com/api/learning/{video}/duration/video/{activity}/{act_token}/{offset}?_ignore_error=true"
                    data = "{}"  # You can modify this if needed
                    response = requests.put(url, headers=headers, data=data)
                    if response.status_code == 200:
                        print("时长已更新,当前值（分钟）：", offset / 60)
                    times = times - 1

                update_video_duration(video, activity, act_token, token)
        else:
            print("二级课程ID获取失败")
            exit()

    print("当前账号刷课全部完成！")

if __name__ == "__main__":
    main()
