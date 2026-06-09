FROM node:20-bookworm AS frontend-build

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM maven:3.9.9-eclipse-temurin-21 AS backend-build

WORKDIR /app
COPY backend/pom.xml backend/pom.xml
RUN cd backend && mvn -DskipTests dependency:go-offline
COPY backend/ backend/
COPY --from=frontend-build /app/frontend/dist/interview-prep-frontend/browser/ backend/src/main/resources/static/
RUN cd backend && mvn -DskipTests package

FROM eclipse-temurin:21-jdk

WORKDIR /app
COPY --from=backend-build /app/backend/target/interview-prep-backend-0.0.1-SNAPSHOT.jar app.jar
COPY backend/data/ backend/data/

ENV APP_DATA_DIR=/app/storage
ENV APP_SEED_DATA_DIR=/app/backend/data

EXPOSE 8082

ENTRYPOINT ["java", "-jar", "app.jar"]
