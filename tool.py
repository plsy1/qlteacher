import requests
import base64


def get_user_input():
    username = input("账号: ")
    password = input("密码: ")
    return username, password


def encode_password(password):
    password_bytes = password.encode("utf-8")
    base64_encoded = base64.b64encode(password_bytes).decode("utf-8")
    return "3" + base64_encoded


def get_token(username, pwd):
    headers = {
        "authorization": "Basic d2ViOnFsdGVhY2hlcg==",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    }

    data = {"username": username, "password": pwd, "grant_type": "password", "pws": "b"}

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

    response = requests.get(
        "https://yxjc.qlteacher.com/api//lesson/lessons/my?projectId=xx2025",
        headers=headers,
    )

    if response.status_code == 200:
        data = response.json()
        data = data["data"]
        lesson_ids = [
            lesson["id"] for topic in data for lesson in topic.get("lessons", [])
        ]
        return lesson_ids
    else:
        print("课程获取失败")
        exit()


def get_video_ids(first_id, token):
    url = f"https://yxjc.qlteacher.com/api//lesson/learning/url?projectId=xx2025&lessonId={first_id}"

    headers = {
        "Authorization": f"Bearer {token}",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    }

    res = requests.get(url, headers=headers)
    link = res.json()["data"]
    id_str = link.split("/")[-1]
    tmp = f"https://player.qlteacher.com/api/learning/{id_str}/course"

    res = requests.get(tmp, headers=headers)
    data = res.json()["data"]

    activity_ids = [
        act["id"]
        for sec in data.get("sections", [])
        for act in sec.get("activitys", [])
    ]

    return id_str, activity_ids


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

    headers = {
        "Authorization": f"Bearer {token}",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    }

    for courseID in course_ids:
        realCourseID, video_ids = get_video_ids(courseID, token)
        for videoID in video_ids:
            print("当前刷课ID：", videoID)
            url = f"https://player.qlteacher.com/api/learning/{realCourseID}/activity/{videoID}"
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
                url = f"https://player.qlteacher.com/api/learning/{realCourseID}/duration/video/{videoID}/{act_token}/{offset}?_ignore_error=true"
                data = "{}"  # You can modify this if needed
                response = requests.put(url, headers=headers, data=data)
                if response.status_code == 200:
                    print("时长已更新,当前值：", offset / 60)
                times = times - 1

            update_video_duration(realCourseID, videoID, act_token, token)

    print("当前账号刷课全部完成！")


if __name__ == "__main__":
    main()
