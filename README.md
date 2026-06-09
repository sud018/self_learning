# Java Full Stack Interview Prep MVP

Full-stack MVP for personal daily Java full-stack interview preparation with points, roadmap, missed-day handling, next-day assignment flow, and a Java coding evaluator.

## Structure

- `backend/` - Spring Boot REST API
- `backend/data/` - local JSON storage instead of a database
- `frontend/` - Angular standalone application

## Personal Mode

Opening the frontend goes directly to the dashboard and saves progress for one personal user in backend data files.

## Daily Training Content

Each day now includes:

- Full preparation notes
- MCQs with scoring
- Written conceptual questions
- Business/backend scenario questions
- Java, Spring Boot, Angular, SQL, and DSA practice
- LeetCode-style coding editors in the Coding Practice section
- Per-problem timer that starts when you click `Solve Coding`

Daily tasks are loaded from `backend/data/curriculum/day-001.json` through `day-090.json`, covering Foundations, Core Java, Collections + SQL, Advanced Java, Spring Boot, Angular, and interview preparation.

## Run Backend

Install Maven if it is not already available, then:

```bash
cd backend
mvn spring-boot:run
```

The API runs at `http://localhost:8082/api`.

## Run Frontend

```bash
cd frontend
npm install
npm start
```

The Angular app runs at `http://localhost:4200`.

## Storage

The MVP saves data in local files:

- `backend/data/curriculum/day-001.json` through `day-090.json`
- `backend/data/progress.txt`
- `backend/data/daily-notes.txt`
- `backend/data/attempts.txt`
- `backend/data/coding-progress.txt`

This is suitable for one local user. For real deployment or multiple people, replace the file store with a database and add proper authentication.

## Deploy On Railway As One Service

This repo includes a root `Dockerfile` and `railway.json` so Railway can deploy the whole app as one service without guessing the monorepo build.

1. Push this repository to GitHub.
2. Create a Railway project from the GitHub repo.
3. Use the root directory of the repo.
4. Add a Railway volume mounted at:

```text
/app/storage
```

5. Railway will run the Docker build:
   - build Angular
   - copy Angular files into Spring Boot static resources
   - package Spring Boot
   - run one Java service

The deployed site will serve both:

- Angular pages such as `/dashboard`, `/coding`, `/missed-day`
- API routes under `/api`

No separate frontend service is required.

## Update The Curriculum

Daily tasks are stored as JSON files in `backend/data/curriculum`.
Edit each `day-XXX.json` file directly to customize notes, MCQs, conceptual questions, coding tasks, SQL, Spring Boot, Angular, and DSA problems.
