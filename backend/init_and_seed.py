from database import init_db
from seed_components import seed_from_folder
from models import Case, Dial, Hands, Strap, Box

def main():
    init_db()
    seed_from_folder(Case, "backend/static/img/case")
    seed_from_folder(Dial, "backend/static/img/dial")
    seed_from_folder(Hands, "backend/static/img/hands")
    seed_from_folder(Strap, "backend/static/img/strap")
    seed_from_folder(Box, "backend/static/img/box")
    print("Baza kreirana i komponente ubačene.")

if __name__ == "__main__":
    main()