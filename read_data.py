import json

# Opening JSON file
file = open("data/person_db.json")

# Loading the JSON File in a dictionary
person_data = json.load(file)

person_data

def load_person_data():
    """A Function that knows where the person database is and returns a dictionary with the persons"""
    file = open("data/person_db.json")
    person_data = json.load(file)
    return person_data

def get_person_list(person_data):
    """A Function that returns a list of the persons names"""
    person_data = load_person_data()
    person_name_list = []
    for person in person_data:
        person_name_list.append(person["firstname"] + ", " + person["lastname"])
    return person_name_list


# Bild einfügen 

def find_person_data_by_name(suchstring):
    """A Function that returns a dictionary with the person data for a given name"""
    # Teilt einen String in und speichert die Ergebnisse in einer Liste
    person_data = load_person_data()
    if suchstring == "None":
        return {}
    
    two_names = suchstring.split(", ")
    vorname = two_names[0]
    nachname = two_names[1]

    for person in person_data:
        if (person["firstname"] == vorname and person["lastname"] == nachname):
            print("Person gefunden: ", person)

            return person
    else:
        return {}



if __name__ == "__main__":
    person_dict = load_person_data()
    person_names = get_person_list(person_dict)
    person = find_person_data_by_name(suchstring="Julian, Huber")
    print(person_names)