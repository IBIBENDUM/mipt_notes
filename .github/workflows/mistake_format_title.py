import os
import re
import requests

def main():
    # Получаем параметры из среды
    github_token = os.getenv('SCRIPT_PAT')
    repo_name = os.getenv('REPO_NAME')
    issue_number = os.getenv('ISSUE_NUMBER')

    if not github_token or not repo_name or not issue_number:
        raise ValueError("Не хватает обязательных параметров: SCRIPT_PAT, REPO_NAME или ISSUE_NUMBER.")

    # Заголовки авторизации
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # URL для работы с API
    issue_url = f"https://api.github.com/repos/{repo_name}/issues/{issue_number}"

    # Получение тела issue
    response = requests.get(issue_url, headers=headers)
    response.raise_for_status()
    issue = response.json()

    # Извлечение тела issue
    body = issue.get("body", "")
    if not body:
        raise ValueError("Тело issue пустое. Убедитесь, что issue создано с корректным шаблоном.")

    # Парсим тело issue
    subject_match = re.search(r"(?i)^### Предмет\s*(.+)$", body, re.MULTILINE)
    error_number_match = re.search(r"(?i)^### Номер с ошибкой\s*(.+)$", body, re.MULTILINE)

    subject = subject_match.group(1).strip() if subject_match else None
    error_number = error_number_match.group(1).strip() if error_number_match else None

    if not subject or not error_number:
        raise ValueError("Не удалось извлечь 'Предмет' или 'Номер с ошибкой' из тела issue.")

    # Формируем новый заголовок
    new_title = f"[{subject}] Ошибка в номере {error_number}"

    # Обновляем заголовок issue
    update_response = requests.patch(
        issue_url,
        headers=headers,
        json={"title": new_title}
    )
    update_response.raise_for_status()

    print(f"Заголовок обновлен на: {new_title}")

if __name__ == "__main__":
    main()
