from app.utils.email import send_test_email

if __name__ == "__main__":
    result = send_test_email()
    if result:
        print("✅ Письмо отправлено! Проверьте почту.")
    else:
        print("❌ Ошибка отправки. Проверьте настройки .env")