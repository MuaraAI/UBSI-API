import { CodeExample } from "@/types";

export const CODE_EXAMPLES: Record<string, CodeExample> = {
  curl: {
    language: "curl",
    title: "cURL",
    snippet: `curl -X GET "https://ubsi-api.muaraai.com/v1/elearning/courses" \\
  -H "X-API-Key: ubsi_secret_key_anda" \\
  -H "Accept: application/json"`,
    response: `{
  "ok": true,
  "data": [
    {
      "code": "101",
      "name": "Dasar Manajemen Bisnis",
      "sks": 3,
      "lecturer": "Dr. Ir. Hendra S., M.Kom",
      "schedule": "Senin, 08:00 - 10:30 WIB",
      "assignments_pending": 0
    },
    {
      "code": "104",
      "name": "Logika & Algoritma",
      "sks": 4,
      "lecturer": "Ahmad Fauzi, M.Kom",
      "schedule": "Selasa, 10:30 - 13:00 WIB",
      "assignments_pending": 1
    },
    {
      "code": "153",
      "name": "Pengantar Teknologi Informasi",
      "sks": 3,
      "lecturer": "Budi Santoso, M.Kom",
      "schedule": "Rabu, 13:30 - 16:00 WIB",
      "assignments_pending": 0
    }
  ],
  "source": "cache",
  "fetched_at": "2026-09-27T10:15:30Z",
  "latency_ms": 238
}`,
    latencyMs: 238,
  },
  python: {
    language: "python",
    title: "Python (requests)",
    snippet: `import requests

headers = {
    "X-API-Key": "ubsi_secret_key_anda"
}

response = requests.get(
    "https://ubsi-api.muaraai.com/v1/elearning/courses", 
    headers=headers
)
data = response.json()
print(f"Total Kursus Aktif: {len(data['data'])}")`,
    response: `{
  "ok": true,
  "data": [
    {
      "code": "101",
      "name": "Dasar Manajemen Bisnis",
      "sks": 3,
      "lecturer": "Dr. Ir. Hendra S., M.Kom",
      "schedule": "Senin, 08:00 - 10:30 WIB"
    },
    {
      "code": "104",
      "name": "Logika & Algoritma",
      "sks": 4,
      "lecturer": "Ahmad Fauzi, M.Kom",
      "schedule": "Selasa, 10:30 - 13:00 WIB"
    }
  ],
  "source": "cache",
  "latency_ms": 242
}`,
    latencyMs: 242,
  },
  typescript: {
    language: "typescript",
    title: "TypeScript (fetch)",
    snippet: `const res = await fetch("https://ubsi-api.muaraai.com/v1/elearning/courses", {
  headers: {
    "X-API-Key": process.env.UBSI_API_KEY!
  },
  next: { revalidate: 60 }
});

const { data } = await res.json();
console.log(data);`,
    response: `{
  "ok": true,
  "data": [
    {
      "code": "101",
      "name": "Dasar Manajemen Bisnis",
      "sks": 3,
      "lecturer": "Dr. Ir. Hendra S., M.Kom",
      "schedule": "Senin, 08:00 - 10:30 WIB"
    }
  ],
  "source": "cache",
  "latency_ms": 229
}`,
    latencyMs: 229,
  },
};
