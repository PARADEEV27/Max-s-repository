@echo off
chcp 1251 > nul
title Установка правильного времени
echo ========================================
echo    Установка правильного времени
echo ========================================
echo.

echo Проверка прав администратора...
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ОШИБКА: Запустите файл от имени Администратора!
    echo Щелкните правой кнопкой -> "Запуск от имени администратора"
    pause
    exit /b 1
)

echo.
echo Текущее время системы:
echo %date% %time%

echo.
echo Синхронизация с сервером времени Microsoft...
w32tm /resync /force

if %errorLevel% equ 0 (
    echo.
    echo ✓ Время успешно синхронизировано!
    echo Новое время системы:
    echo %date% %time%
) else (
    echo.
    echo ✗ Ошибка синхронизации. Пробуем альтернативный метод...
    
    echo Обновление конфигурации времени...
    w32tm /config /update /manualpeerlist:"time.windows.com,0x8 time.nist.gov,0x8 pool.ntp.org,0x8" /syncfromflags:manual /reliable:yes
    
    echo Перезапуск службы времени...
    net stop w32time >nul 2>&1
    net start w32time >nul 2>&1
    
    echo Повторная синхронизация...
    w32tm /resync /force
    
    if %errorLevel% equ 0 (
        echo.
        echo ✓ Время успешно синхронизировано!
        echo Новое время системы:
        echo %date% %time%
    ) else (
        echo.
        echo ✗ Не удалось автоматически синхронизировать время.
        echo Запустите синхронизацию вручную через Панель управления
    )
)

echo.
echo Проверка настроек часового пояса...
echo Текущий часовой пояс: 
systeminfo | findstr /C:"Time Zone"

echo.
echo Для ручной настройки часового пояса:
echo 1. Нажмите Win + R
echo 2. Введите: timedate.cpl
echo 3. Выберите правильный часовой пояс

echo.
pause