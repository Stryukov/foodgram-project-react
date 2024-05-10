#  Foodgram
Это приложения для публикации рецептов, которыми можно поделиться или сохранить. 

Возможности приложения: 
- публикация рецепта (фото, описание, ингредиенты, время приготовления)
- избранные рецепты
- подписка на авторов
- экспорт списка покупок для выбранных рецептов

## Environment Variables
Пример файла переменных окружения - infra/.env.example

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

**Server:** Django, DRF, Nginx, Docker, Postgres


## Authors

- [@stryukov](https://www.github.com/stryukov)
