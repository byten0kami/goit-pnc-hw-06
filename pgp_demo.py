#!/usr/bin/env python3
"""
Лабораторна робота: Використання PGP (Pretty Good Privacy)
для захисту електронних листів.

Демонстрація повного циклу PGP:
- Генерація ключових пар
- Експорт та обмін публічними ключами
- Підписання повідомлень
- Шифрування повідомлень
- Розшифрування та перевірка підписів
"""

import os
import shutil
import subprocess
import tempfile


def run_gpg(homedir, args, input_data=None):
    """Виконує gpg з вказаним homedir та аргументами."""
    cmd = ["gpg", "--homedir", homedir, "--batch", "--yes",
           "--trust-model", "always"] + args
    result = subprocess.run(
        cmd, input=input_data, capture_output=True, text=True
    )
    return result


def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")


def print_step(text):
    print(f"\n--- {text} ---")


def main():
    print_header("PGP Demo — Лабораторна робота з ЕЦП")
    print("Використання PGP для підписання та шифрування листів")
    print(f"GnuPG: {subprocess.getoutput('gpg --version | head -1')}")

    # Створюємо тимчасові директорії для двох студентів
    base_tmp = tempfile.mkdtemp(prefix="pgp_demo_")
    home_a = os.path.join(base_tmp, "student_a")
    home_b = os.path.join(base_tmp, "student_b")
    os.makedirs(home_a, mode=0o700)
    os.makedirs(home_b, mode=0o700)

    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)

    try:
        # ═══════════════════════════════════════════════
        # КРОК 1: Генерація ключів
        # ═══════════════════════════════════════════════
        print_step("Крок 1: Генерація ключів PGP")

        # Студент А
        print("\nСтудент А: генерація ключової пари RSA-4096...")
        key_params_a = """\
%no-protection
Key-Type: RSA
Key-Length: 4096
Subkey-Type: RSA
Subkey-Length: 4096
Name-Real: Oleksandr Kovalenko
Name-Email: student_a@university.edu.ua
Name-Comment: Student A - PGP Lab
Expire-Date: 1y
%commit
"""
        result = run_gpg(home_a, ["--gen-key"], input_data=key_params_a)
        if result.returncode == 0:
            print("✓ Ключову пару Студента А створено успішно")
        else:
            print(f"Помилка: {result.stderr}")
            return

        # Студент Б
        print("\nСтудент Б: генерація ключової пари RSA-4096...")
        key_params_b = """\
%no-protection
Key-Type: RSA
Key-Length: 4096
Subkey-Type: RSA
Subkey-Length: 4096
Name-Real: Mariya Shevchenko
Name-Email: student_b@university.edu.ua
Name-Comment: Student B - PGP Lab
Expire-Date: 1y
%commit
"""
        result = run_gpg(home_b, ["--gen-key"], input_data=key_params_b)
        if result.returncode == 0:
            print("✓ Ключову пару Студента Б створено успішно")
        else:
            print(f"Помилка: {result.stderr}")
            return

        # Перегляд ключів
        print("\nКлючі Студента А:")
        result = run_gpg(home_a, ["--list-keys", "--keyid-format", "long"])
        print(result.stdout.strip())

        print("\nКлючі Студента Б:")
        result = run_gpg(home_b, ["--list-keys", "--keyid-format", "long"])
        print(result.stdout.strip())

        # ═══════════════════════════════════════════════
        # КРОК 2: Експорт публічних ключів
        # ═══════════════════════════════════════════════
        print_step("Крок 2: Експорт публічних ключів")

        # Експорт ключа Студента А
        result_a = run_gpg(home_a, [
            "--armor", "--export", "student_a@university.edu.ua"
        ])
        pubkey_a = result_a.stdout
        pubkey_a_path = os.path.join(output_dir, "student_a_public.asc")
        with open(pubkey_a_path, "w") as f:
            f.write(pubkey_a)
        print(f"✓ Публічний ключ Студента А збережено: student_a_public.asc")
        # Показуємо початок ключа
        lines = pubkey_a.strip().split("\n")
        for line in lines[:5]:
            print(f"  {line}")
        print(f"  ... ({len(lines)} рядків)")
        for line in lines[-2:]:
            print(f"  {line}")

        # Експорт ключа Студента Б
        result_b = run_gpg(home_b, [
            "--armor", "--export", "student_b@university.edu.ua"
        ])
        pubkey_b = result_b.stdout
        pubkey_b_path = os.path.join(output_dir, "student_b_public.asc")
        with open(pubkey_b_path, "w") as f:
            f.write(pubkey_b)
        print(f"\n✓ Публічний ключ Студента Б збережено: student_b_public.asc")

        # ═══════════════════════════════════════════════
        # КРОК 3: Обмін ключами (імпорт)
        # ═══════════════════════════════════════════════
        print_step("Крок 3: Обмін публічними ключами")

        # Студент А імпортує ключ Студента Б
        result = run_gpg(home_a, ["--import", pubkey_b_path])
        print("Студент А імпортує ключ Студента Б:")
        stderr_lines = result.stderr.strip().split("\n")
        for line in stderr_lines:
            if "imported" in line or "processed" in line:
                print(f"  {line.strip()}")
        print("✓ Ключ Студента Б імпортовано до Студента А")

        # Студент Б імпортує ключ Студента А
        result = run_gpg(home_b, ["--import", pubkey_a_path])
        print("\nСтудент Б імпортує ключ Студента А:")
        stderr_lines = result.stderr.strip().split("\n")
        for line in stderr_lines:
            if "imported" in line or "processed" in line:
                print(f"  {line.strip()}")
        print("✓ Ключ Студента А імпортовано до Студента Б")

        # Перевірка ключів після обміну
        print("\nКлючі Студента А після імпорту:")
        result = run_gpg(home_a, ["--list-keys", "--keyid-format", "short"])
        print(result.stdout.strip())

        # ═══════════════════════════════════════════════
        # КРОК 4: Підписання повідомлення
        # ═══════════════════════════════════════════════
        print_step("Крок 4: Підписання повідомлення (цифровий підпис)")

        message_text = (
            "Тема: ЕЦП та його застосування\n\n"
            "Електронно-цифровий підпис (ЕЦП) — це криптографічний механізм,\n"
            "який забезпечує автентичність, цілісність та неспростовність\n"
            "електронних документів і повідомлень.\n\n"
            "Основні сфери застосування ЕЦП:\n"
            "1. Електронний документообіг\n"
            "2. Електронна комерція\n"
            "3. Електронне урядування (е-Gov)\n"
            "4. Захист електронної пошти (PGP/GPG)\n"
            "5. Підписання програмного забезпечення\n\n"
            "З повагою,\n"
            "Олександр Коваленко (Студент А)"
        )

        message_path = os.path.join(output_dir, "message.txt")
        with open(message_path, "w") as f:
            f.write(message_text)

        print("Оригінальне повідомлення:")
        for line in message_text.split("\n"):
            print(f"  | {line}")

        # Очищений підпис (clearsign)
        signed_path = os.path.join(output_dir, "message_signed.asc")
        result = run_gpg(home_a, [
            "--clearsign",
            "--local-user", "student_a@university.edu.ua",
            "--output", signed_path,
            message_path
        ])
        if result.returncode == 0:
            print("\n✓ Повідомлення підписано (clearsign)")
            with open(signed_path) as f:
                signed_content = f.read()
            signed_lines = signed_content.strip().split("\n")
            for line in signed_lines[:3]:
                print(f"  {line}")
            print("  [текст повідомлення]")
            for line in signed_lines[-4:]:
                print(f"  {line}")
        else:
            print(f"Помилка: {result.stderr}")

        # ═══════════════════════════════════════════════
        # КРОК 5: Шифрування повідомлення
        # ═══════════════════════════════════════════════
        print_step("Крок 5: Шифрування та підписання повідомлення")

        encrypted_path = os.path.join(output_dir, "message_encrypted.asc")
        result = run_gpg(home_a, [
            "--armor",
            "--sign",
            "--encrypt",
            "--local-user", "student_a@university.edu.ua",
            "--recipient", "student_b@university.edu.ua",
            "--output", encrypted_path,
            message_path
        ])

        if result.returncode == 0:
            print("✓ Повідомлення зашифровано ключем Студента Б та підписано ключем Студента А")
            with open(encrypted_path) as f:
                enc_content = f.read()
            enc_lines = enc_content.strip().split("\n")
            print(f"\nЗашифрований лист ({len(enc_lines)} рядків):")
            for line in enc_lines[:5]:
                print(f"  {line}")
            print("  ...")
            for line in enc_lines[-2:]:
                print(f"  {line}")
        else:
            print(f"Помилка: {result.stderr}")

        # ═══════════════════════════════════════════════
        # КРОК 6: Розшифрування та перевірка підпису
        # ═══════════════════════════════════════════════
        print_step("Крок 6: Розшифрування та перевірка підпису (Студент Б)")

        decrypted_path = os.path.join(output_dir, "message_decrypted.txt")
        result = run_gpg(home_b, [
            "--decrypt",
            "--output", decrypted_path,
            encrypted_path
        ])

        if result.returncode == 0:
            with open(decrypted_path) as f:
                decrypted_text = f.read()
            print("✓ Повідомлення розшифровано успішно!")
            print("\nРозшифрований текст:")
            for line in decrypted_text.split("\n"):
                print(f"  | {line}")

            # Інформація про підпис
            print("\nПеревірка цифрового підпису:")
            for line in result.stderr.split("\n"):
                line = line.strip()
                if "Good signature" in line or "Correct signature" in line:
                    print(f"  ✓ {line}")
                elif "Signature made" in line or "signature" in line.lower():
                    if line:
                        print(f"  {line}")
        else:
            print(f"Помилка: {result.stderr}")

        # ═══════════════════════════════════════════════
        # КРОК 7: Відповідь Студента Б
        # ═══════════════════════════════════════════════
        print_step("Крок 7: Студент Б надсилає зашифровану відповідь")

        reply_text = (
            "Тема: Re: ЕЦП та його застосування\n\n"
            "Дякую за інформативний лист!\n\n"
            "Додаю ще кілька важливих застосувань ЕЦП:\n"
            "- Blockchain та криптовалюти\n"
            "- Смарт-контракти\n"
            "- Захист IoT пристроїв\n"
            "- Медичні електронні записи\n\n"
            "З повагою,\n"
            "Марія Шевченко (Студент Б)"
        )

        reply_path = os.path.join(output_dir, "reply.txt")
        with open(reply_path, "w") as f:
            f.write(reply_text)

        reply_enc_path = os.path.join(output_dir, "reply_encrypted.asc")
        result = run_gpg(home_b, [
            "--armor", "--sign", "--encrypt",
            "--local-user", "student_b@university.edu.ua",
            "--recipient", "student_a@university.edu.ua",
            "--output", reply_enc_path,
            reply_path
        ])
        if result.returncode == 0:
            print("✓ Відповідь зашифровано та підписано Студентом Б")

        # Студент А розшифровує відповідь
        print("\nСтудент А розшифровує відповідь:")
        reply_dec_path = os.path.join(output_dir, "reply_decrypted.txt")
        result = run_gpg(home_a, [
            "--decrypt", "--output", reply_dec_path, reply_enc_path
        ])
        if result.returncode == 0:
            with open(reply_dec_path) as f:
                reply_dec = f.read()
            print("✓ Відповідь розшифровано успішно!")
            for line in reply_dec.split("\n"):
                print(f"  | {line}")
            for line in result.stderr.split("\n"):
                line = line.strip()
                if "Good signature" in line or "Correct signature" in line:
                    print(f"\n  ✓ {line}")

        # ═══════════════════════════════════════════════
        # КРОК 8: Перевірка clearsign підпису
        # ═══════════════════════════════════════════════
        print_step("Крок 8: Перевірка відокремленого підпису")

        result = run_gpg(home_b, ["--verify", signed_path])
        print("Студент Б перевіряє підпис на повідомленні:")
        for line in result.stderr.split("\n"):
            line = line.strip()
            if line:
                print(f"  {line}")

        # ═══════════════════════════════════════════════
        # ПІДСУМОК
        # ═══════════════════════════════════════════════
        print_header("ПІДСУМОК")
        print("\nПродемонстровано повний цикл PGP:")
        print("✓ 1. Генерація ключових пар RSA-4096 для двох учасників")
        print("✓ 2. Експорт публічних ключів у форматі ASCII (.asc)")
        print("✓ 3. Обмін та імпорт публічних ключів")
        print("✓ 4. Підписання повідомлення (clearsign)")
        print("✓ 5. Шифрування + підписання листа")
        print("✓ 6. Розшифрування та перевірка підпису")
        print("✓ 7. Двостороння зашифрована комунікація")
        print("✓ 8. Перевірка відокремленого підпису")

        print(f"\nФайли збережено у: {output_dir}/")
        for f in sorted(os.listdir(output_dir)):
            size = os.path.getsize(os.path.join(output_dir, f))
            print(f"  {f} ({size} байт)")

    finally:
        # Очищення тимчасових директорій
        shutil.rmtree(base_tmp, ignore_errors=True)
        print(f"\n✓ Тимчасові ключі видалено")


if __name__ == "__main__":
    main()
