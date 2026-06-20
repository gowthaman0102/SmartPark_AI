from pathlib import Path
import gdown


def download_assets():

    base_dir = Path(__file__).resolve().parent.parent

    data_dir = base_dir / "data"
    model_dir = base_dir / "models"

    data_dir.mkdir(exist_ok=True)
    model_dir.mkdir(exist_ok=True)

    csv_file = data_dir / "parking_violations.csv"
    model_file = model_dir / "congestion_model.pkl"

    print(f"DATA DIR: {data_dir}")
    print(f"MODEL DIR: {model_dir}")

    if not csv_file.exists():
        print("Downloading parking_violations.csv...")

        gdown.download(
            "https://drive.google.com/uc?id=1H6K28r7wMEW9uttzsomrF66K2z6uKYX3",
            str(csv_file),
            quiet=False
        )

    if not model_file.exists():
        print("Downloading congestion_model.pkl...")

        gdown.download(
            "https://drive.google.com/uc?id=1Mz8ZJlnejAZoL_ZCFtBQc266aj1yjg3b",
            str(model_file),
            quiet=False
        )

    print("CSV Exists:", csv_file.exists())
    print("MODEL Exists:", model_file.exists())
