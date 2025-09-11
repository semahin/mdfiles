import requests
import xml.etree.ElementTree as ET
from requests.auth import HTTPBasicAuth

NEXTCLOUD_URL = "http://158.160.175.31:8080" # todo
USERNAME = "admin"
APP_PASSWORD = "Admin123!"

headers = {"OCS-APIRequest": "true"}

correct_answers_global = { #todo
    '2 + 2 = ?': '4',
    '1 + 3': '4',
    '0 + 4': '4'
}

forms_url = f"{NEXTCLOUD_URL}/ocs/v2.php/apps/forms/api/v3/forms"
resp = requests.get(forms_url, headers=headers, auth=HTTPBasicAuth(USERNAME, APP_PASSWORD))
root = ET.fromstring(resp.text)

forms = root.findall(".//data/element")
if not forms:
    print("Формы не найдены")
    exit()

md_lines = ["|Пользователи|Результаты|",
            "|-|-|"]

stats = {}  # user -> {"correct": int, "total": int}

for form in forms:
    form_id = form.find("id").text
    form_title = form.find("title").text or f"Form {form_id}"

    # Получаем submissions формы
    sub_url = f"{NEXTCLOUD_URL}/ocs/v2.php/apps/forms/api/v3/forms/{form_id}/submissions"
    sub_resp = requests.get(sub_url, headers=headers, auth=HTTPBasicAuth(USERNAME, APP_PASSWORD))
    sub_root = ET.fromstring(sub_resp.text)

    # Словарь вопросов: questionId -> текст вопроса
    questions = {q.find("id").text: q.find("text").text for q in sub_root.findall(".//questions/element")}

    for s in sub_root.findall(".//submissions/element"):
        user = s.find("userDisplayName").text
        answers = s.findall(".//answers/element")

        correct_count = 0
        total_questions = len(correct_answers_global)
        for ans in answers:
            qid = ans.find("questionId").text
            value = ans.find("text").text
            question_text = questions.get(qid, None)
            if question_text and correct_answers_global.get(question_text) == value:
                correct_count += 1

        if user not in stats:
            stats[user] = {"correct": 0, "total": 0}
        stats[user]["correct"] += correct_count
        stats[user]["total"] += total_questions

for user, result in stats.items():
    percent = round(result["correct"] / result["total"] * 100) if result["total"] else 0
    md_lines.append(f"| {user} | {percent}% |")

with open("results_all_forms.md", "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

print("Markdown с результатами всех форм создан: results_all_forms.md")
