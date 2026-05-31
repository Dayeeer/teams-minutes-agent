from app.auth_token_cache import acquire_cached_delegated_token
from app.workers.pipeline_worker import run_pipeline


def main():
    access_token = acquire_cached_delegated_token()

    result = run_pipeline(
        access_token=access_token,
        days_back=1,
        days_forward=30,
        user_id=None,
    )

    print(result)


if __name__ == "__main__":
    main()
