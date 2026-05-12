# starter-cli — питон CLI стартер

Для задач, где надо "обработать файл/поток данных, вывести результат".

## Запуск

```bash
./main.py input.txt
./main.py input.txt --json
cat input.txt | ./main.py -
```

## Что менять

- функция `process(text)` — твоя логика
- если нужны ещё аргументы — добавь в `argparse`
