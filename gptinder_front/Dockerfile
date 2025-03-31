FROM node:20-alpine as build

WORKDIR /app

# Установка зависимостей
COPY package*.json ./
RUN npm install

# Копирование кода приложения
COPY . .

# Сборка приложения
RUN npm run build

# Рабочий образ
FROM nginx:alpine

# Копирование собранного приложения из предыдущего этапа
COPY --from=build /app/dist /usr/share/nginx/html

# Копирование конфигурации nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"] 