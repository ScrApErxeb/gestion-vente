from app import create_app

app = create_app()

if __name__ == "__main__":
    # Pour tests locaux uniquement
    app.run(host="127.0.0.1", port=5000)
