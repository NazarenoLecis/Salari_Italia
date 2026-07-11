from __future__ import annotations

from salari_italia.pipeline import run_pipeline


def main() -> None:
    data, report = run_pipeline()
    print(f"Righe create: {len(data)}")
    print(f"Richieste riuscite: {report['successful_requests']}")
    print(f"Richieste fallite: {report['failed_requests']}")
    for error in report["errors"]:
        print(f"- {error['request']}: {error['error']}")


if __name__ == "__main__":
    main()
