import json
from pathlib import Path
from datetime import datetime


def export_results_to_json(
    output_path: str,
    metadata: dict,
    harvest_summary: dict,
    reliability_table,
):
    """
    Export MCS Rainwater Harvesting results to a JSON file.

    Parameters
    ----------
    output_path : str
        Folder or file path where JSON will be saved
    metadata : dict
        Study / school / parameter information
    harvest_summary : dict
        Annual, monthly, weekly harvest summaries (PER YEAR)
    reliability_table : pandas.DataFrame
        Tank size vs reliability results
    """

    # Ensure path
    output_path = Path(output_path)
    if output_path.suffix != ".json":
        output_path = output_path / "mcs_rwh_results.json"

    payload = {
        "generated_at": datetime.now().isoformat(),
        "metadata": metadata,
        "harvest_summary": {
            "annual_L_per_year": round(harvest_summary["annual_L"], 2),
            "monthly_L_per_year": {
                str(k): round(v, 2)
                for k, v in harvest_summary["monthly_L"].items()
            },
            "weekly_L_per_year": {
                str(k): round(v, 2)
                for k, v in harvest_summary["weekly_L"].items()
            },
        },
        "tank_reliability": reliability_table.to_dict(orient="records"),
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    return str(output_path)
