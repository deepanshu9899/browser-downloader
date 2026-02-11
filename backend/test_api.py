from fastapi.testclient import TestClient

import main


class FakeRedis:
    def __init__(self):
        self.items = []

    def rpush(self, key, value):
        self.items.append((key, value))

    def llen(self, key):
        return len([x for x in self.items if x[0] == key])


def test_generate_resume_and_queue():
    fake = FakeRedis()
    main._redis = lambda: fake

    client = TestClient(main.app)

    resume_resp = client.post(
        "/api/resume/generate",
        json={
            "profile": {
                "full_name": "Alex Doe",
                "email": "alex@example.com",
                "title": "Engineer",
                "summary": "Builds platforms",
                "skills": ["Python", "Kubernetes"],
                "experience": ["Built APIs"],
                "preferred_roles": ["Backend Engineer"],
            },
            "target_role": "Backend Engineer",
            "target_company": "Contoso",
            "keywords": ["python", "kubernetes"],
        },
    )

    assert resume_resp.status_code == 200
    resume_data = resume_resp.json()

    queue_resp = client.post(
        "/api/jobs/auto-apply",
        json={
            "resume_id": resume_data["resume_id"],
            "resume_text": resume_data["content"],
            "jobs": [
                {
                    "company": "Contoso",
                    "role": "Backend Engineer",
                    "location": "Remote",
                    "description": "python kubernetes backend",
                    "apply_url": "https://example.test/apply",
                }
            ],
            "auto_submit": True,
        },
    )

    assert queue_resp.status_code == 200
    assert queue_resp.json()["queued"] == 1

    size_resp = client.get("/api/jobs/queue-size")
    assert size_resp.status_code == 200
    assert size_resp.json()["size"] == 1
