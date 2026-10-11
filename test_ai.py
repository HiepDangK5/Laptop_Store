"""Chạy 10 câu hỏi mẫu qua Gemini: python test_ai.py"""

import json
import sys

from app.services.ai_service import extract_filters

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


SAMPLES = [
    {
        "question": "Mình là sinh viên IT, ngân sách tối đa 25 triệu, muốn máy nhẹ.",
        "checks": {"need_clarify": False, "min_ram_at_least": 16},
    },
    {
        "question": "Tôi cần laptop gaming dưới 35 triệu.",
        "checks": {"need_clarify": False, "need_dedicated_gpu": True},
    },
    {
        "question": "Dùng đồ họa và dựng video, ngân sách khoảng 30 triệu.",
        "checks": {"need_clarify": False, "need_dedicated_gpu": True},
    },
    {
        "question": "Laptop văn phòng dưới 18 triệu, ưu tiên nhẹ và pin lâu.",
        "checks": {"need_clarify": False, "max_weight_at_most": 1.6},
    },
    {
        "question": "Lập trình, từ 20 đến 30 triệu, RAM ít nhất 32GB.",
        "checks": {"need_clarify": False, "min_ram_at_least": 32},
    },
    {
        "question": "Tư vấn cho tôi một chiếc laptop.",
        "checks": {"need_clarify": True},
    },
    {
        "question": "Ngân sách của tôi là 15 triệu.",
        "checks": {"need_clarify": True},
    },
    {
        "question": "Tôi là sinh viên, cần máy để học và lập trình cơ bản.",
        "checks": {"need_clarify": True},
    },
    {
        "question": "Chơi game và học IT, tối đa 40 triệu.",
        "checks": {"need_clarify": False, "min_ram_at_least": 16, "need_dedicated_gpu": True},
    },
    {
        "question": "Ưu tiên Lenovo.",
        "history": [
            {"role": "user", "content": "Tôi cần máy làm đồ họa, ngân sách tối đa 25 triệu."}
        ],
        "checks": {"need_clarify": False, "need_dedicated_gpu": True},
    },
]


def check_result(result: dict, checks: dict) -> list[str]:
    errors = []
    if checks.get("need_clarify") is not None and result["need_clarify"] != checks["need_clarify"]:
        errors.append(f"need_clarify cần là {checks['need_clarify']}")
    if checks.get("need_dedicated_gpu") and not result["need_dedicated_gpu"]:
        errors.append("cần yêu cầu GPU rời")
    if result["min_ram_gb"] is None and "min_ram_at_least" in checks:
        errors.append("thiếu min_ram_gb")
    elif "min_ram_at_least" in checks and result["min_ram_gb"] < checks["min_ram_at_least"]:
        errors.append(f"min_ram_gb cần >= {checks['min_ram_at_least']}")
    if "max_weight_at_most" in checks and (
        result["max_weight_kg"] is None or result["max_weight_kg"] > checks["max_weight_at_most"]
    ):
        errors.append(f"max_weight_kg cần <= {checks['max_weight_at_most']}")
    return errors


def main():
    failed = 0
    for number, sample in enumerate(SAMPLES, start=1):
        print(f"\n[{number}/10] {sample['question']}")
        try:
            result = extract_filters(sample["question"], history=sample.get("history", []))
            errors = check_result(result, sample["checks"])
            print(json.dumps(result, ensure_ascii=False, indent=2))
            if errors:
                failed += 1
                print("KẾT QUẢ: FAIL - " + "; ".join(errors))
            else:
                print("KẾT QUẢ: PASS")
        except Exception as error:
            failed += 1
            print(f"KẾT QUẢ: ERROR - {error}")

    print(f"\nHoàn tất: {len(SAMPLES) - failed}/{len(SAMPLES)} câu đạt kiểm tra.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
