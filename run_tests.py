#!/usr/bin/env python
import os
import sys
import subprocess


def run_tests():
    """Запуск тестов с покрытием"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.test_settings')

    # Запуск тестов с покрытием
    result = subprocess.run([
        'coverage', 'run', '--source=.', 'manage.py', 'test',
        '--settings=config.test_settings'
    ])

    if result.returncode == 0:
        # Генерация отчета о покрытии
        subprocess.run(['coverage', 'report', '--show-missing'])
        subprocess.run(['coverage', 'html'])
        print("\nОтчет о покрытии сохранен в htmlcov/")
    else:
        print("Тесты завершились с ошибками")

    return result.returncode


def run_flake8():
    """Запуск проверки стиля кода"""
    print("Запуск Flake8...")
    result = subprocess.run(['flake8', '--exclude=migrations', '--max-line-length=120'])

    if result.returncode == 0:
        print("✓ Flake8 проверка пройдена")
    else:
        print("✗ Flake8 проверка не пройдена")

    return result.returncode


if __name__ == '__main__':
    print("Запуск тестов...")
    test_exit_code = run_tests()

    print("\nЗапуск проверки стиля кода...")
    flake8_exit_code = run_flake8()

    if test_exit_code == 0 and flake8_exit_code == 0:
        print("\nВсе проверки пройдены успешно!")
        sys.exit(0)
    else:
        print("\nНекоторые проверки не пройдены")
        sys.exit(1)
