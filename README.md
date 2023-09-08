#  Foodgram
Это приложения для публикации рецептов, которыми можно поделиться или сохранить. 

Возможности приложения: 
- публикация рецепта (фото, описание, ингредиенты, время приготовления)
- избранные рецепты
- подписка на авторов
- экспорт списка покупок для выбранных рецептов

## Environment Variables
Пример файла переменных окружения - infra/.env.example

## Demo

URL front: [https://foodgram-55.hopto.org](https://foodgram-55.hopto.org) 

URL admin panel: [https://foodgram-55.hopto.org/admin](https://foodgram-55.hopto.org/admin)

Admin:
- login: admin
- email: admin@mail.com
- password: a

User1:
- login: ivan
- email: ivan@mail.com
- password: 000000Qq

User2:
- login: boris
- email: boris@mail.com
- password: 000000Qq


## Deployment

Клонируй проект

```bash
  git clone git@github.com:Stryukov/foodgram-project-react.git
```
Переходи в каталог проекта

```bash
  cd infra
```
Собери и запусти контейнеры

```bash
  docker compose up --build
```

## Tech Stack

**Client:** React

**Server:** Django, DRF


## Authors

- [@stryukov](https://www.github.com/stryukov)
