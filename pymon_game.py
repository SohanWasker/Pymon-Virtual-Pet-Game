
"""
Student id : s4098345
Highest Level Attempted (P/C/D/HD): DI

- Reflection: 
  In this assignment I learned about the following:
  1. Development of reusable solutions using object oriented programming.
  2. Making algorithmic solutions and coding them.
"""

import random
import csv 


def generate_random_number(max_number=1):
    r=random.randint(0,max_number)
    return r 

# Custom exception for invalid directions
class InvalidDirectionException(Exception):
    pass
# Custom exception for invalid file formats
class InvalidInputFileFormat(Exception):
    pass

class Item:
    def __init__(self, name, description, pickable='yes', consumable='yes'):
        self.name=name
        self.description=description
        self.pickable=pickable
        self.consumable=consumable

    def use(self, pymon):
        pass

class Apple(Item):
    def __init__(self):
        super().__init__(name="apple", description="A fresh apple that can restore energy.")

    def use(self, pymon):
        if "apple" in pymon.inventory:
            if pymon.energy<3:
                pymon.energy+=1
                pymon.inventory.remove("apple")
                print(f"{pymon.name}'s energy increased to {pymon.energy}.")
            else:
                print(f"{pymon.name}'s energy is already full!")
        else:
            print("You don't have any apples to use.")

class MagicPotion(Item):
    def __init__(self):
        super().__init__(name="Magic Potion", description="Grants immunity in battle.")

    def use(self, pymon):
        pymon.immunity=True
        pymon.inventory.remove("Magic Potion")
        print(f"{pymon.name} is now immune for the next battle.")

class Binoculars(Item):
    def __init__(self):
        super().__init__(name="binoculars", description="Allows you to see surroundings.")

    def use(self, pymon):
        print(f"With the binoculars, you can see the surroundings of {pymon.current_location.get_name()}:")
        for direction, location in pymon.current_location.doors.items():
            if location != 'None':
                print(f"{direction.capitalize()}: {location.get_name()}")

class Tree(Item):
    def __init__(self):
        super().__init__(name="tree", description="A decorative tree.",pickable='no')

class Creature:
    def __init__(self,name,description):
        self.name=name
        self.description=description
        self.current_location=None
        self.adoptable='no'
    
    def set_location(self,location):
        self.current_location=location

class Pymon(Creature):
    def __init__(self, name="The player", description="Wild Pymon",adoptable='yes'):
        self.name=name
        self.description=description
        self.current_location = None
        self.energy=3
        self.inventory=[]  # Contains picked items
        self.immunity=False # Checks if the pymon has imunity for battling
        self.adoptable=adoptable
        self.msld=0 
    
    def move(self, direction='None'):
        if self.current_location!=None:
            if self.current_location.doors[direction]!='None':
                try:
                    self.current_location=self.current_location.doors[direction]
                    print(f"{self.name} moved {direction} to {self.current_location.get_name()}.")
                    self.msld+=1

                    # Decreasing the energy after every 2 moves
                    if self.msld>=2:
                        self.energy-=1
                        self.msld=0
                        print(f"{self.name}'s energy decreased to {self.energy}.")

                    # Releasing pymon in the wild after energy=0
                    if self.energy<=0:
                        print(f"{self.name} ran out of energy and escaped into the wild!")
                        self.relinquish()

                except InvalidDirectionException as e:
                    print(f"Move failed: {e}")
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
            else:
                print("no access to "+direction)
                
    def spawn(self, loc):
        if loc!=None:
            loc.add_creature(self)
            self.current_location=loc

    def pick_item(self, item_name):
        for item in self.current_location.items:
            if item.name==item_name and item.pickable!="no":
                self.inventory.append(item.name)
                self.current_location.items.remove(item)
                print(f"Picked up {item_name}.")
                return
        print(f"{item_name} is not available to pick up.")

    def use_item(self, item_name):
        for item in self.inventory:
            if item==item_name:
                if item_name=="apple":
                    Apple().use(self)
                elif item_name=="Magic Potion":
                    MagicPotion().use(self)
                elif item_name=="binocular":
                    Binoculars().use(self)
                break
        else:
            print(f"{item_name} is not in your inventory!")

    def view_inventory(self):
        if not self.inventory:
            print("Inventory is empty.")
        else:
            print("Inventory:")
            for idx, item_name in enumerate(self.inventory, 1):
                print(f"{idx}.{item_name}")

            use_item_choice=input("Would you like to use an item? (y/n): ").lower()
            if use_item_choice=='y':
                try:
                    item_index=int(input("Select the item Number you wish to use: "))-1
                    if 0<=item_index<len(self.inventory):
                        selected_item=self.inventory[item_index]
                        self.use_item(selected_item)
                        print(f"You used {selected_item}!")
                    else:
                        print("Invalid item selection.")
                except ValueError:
                    print("Please enter a valid item number.")

    def challenge(self, creature, benched_pymons, locations):
        choices=["rock", "paper", "scissors"]
        pymon_score=0
        opponent_score=0
        self.energy=3
 
        while self.energy>0:
            pymon_choice=input("Choose rock, paper, or scissors: ").lower()
            if pymon_choice not in choices:
                print("Invalid choice. Try again.")
                continue

            opponent_choice=random.choice(choices)
            print(f"{creature.name} chose {opponent_choice}")

            if pymon_choice==opponent_choice:
                print("It's a draw!")
            elif (pymon_choice=="rock" and opponent_choice=="scissors") or \
                 (pymon_choice=="paper" and opponent_choice=="rock") or \
                 (pymon_choice=="scissors" and opponent_choice=="paper"):
                pymon_score+=1
                print("You win this round!")
            else:
                opponent_score+=1
                self.energy-=1 if not self.immunity else 0
                print("You lost this round.")

            if pymon_score==2 or opponent_score==2:
                break

        if pymon_score>opponent_score:
            print(f"{self.name} wins the battle!")
            # Captures the opposing pymon as a pet
            benched_pymons.append(creature)
            print(f"{creature.name} has been added to your pet list!")
        else:
            print(f"{self.name} lost the battle.")
            # Releasing the current Pymon to a random location
            self.relinquish(locations, benched_pymons)

    def relinquish(self, locations, benched_pymons):
        random_location=random.choice(locations)
        random_location.add_creature(self)
        print(f"{self.name} has been released into the wild at {random_location.get_name()}.")
        if not self.energy:
            print("Game Over!")
            exit()

        # Checking for another Pymon in the pet list
        if benched_pymons:
            new_pymon=benched_pymons.pop(0)
            new_pymon.current_location=self.current_location
            self.current_location=random_location
            print(f"{new_pymon.name} is now your new active Pymon.")
            return new_pymon 
        else:
            print("You have no more Pymons left. Game over!")
            exit()
            
    def get_location(self):
        return self.current_location
    
    def inspect(self):
        print(f"Pymon Name:{self.name}")
        print(f"Description:{self.description}")
        print(f"Energy:{self.energy}")
        if self.current_location:
            print(f"Current Location:{self.current_location.get_name()}")
        else:
            print("Not currently in any location.")
            
class Location:
    def __init__(self, name="New room", description='new room', w=None, n=None , e=None, s=None):
        self.name=name
        self.description=description
        self.doors={}
        self.doors["west"]=w
        self.doors["north"]=n
        self.doors["east"]=e
        self.doors["south"]=s
        self.creatures=[]
        self.items=[]
        
    def add_creature(self, creature):
        self.creatures.append(creature)
        
    def add_item(self, item):
        self.items.append(item)
        
    def connect_east(self, another_room):
        self.doors["east"]=another_room 
        another_room.doors["west"]=self;
        
    def connect_west(self, another_room):
        self.doors["west"]=another_room 
        another_room.doors["east"]=self;
    
    def connect_north(self, another_room):
        self.doors["north"]=another_room 
        another_room.doors["south"]=self;
        
    def connect_south(self, another_room):
        self.doors["south"]=another_room 
        another_room.doors["north"]=self;
        
    def get_name(self):
        return self.name
    


def move_pymon(self):
        direction=input("Enter direction (west, north, east, south): ").lower()
        try:
            self.current_pymon.move(direction)
        except InvalidDirectionException as e:
            print(e)

def inspect_location(self):
    location=self.current_pymon.current_location
    print(f"Location: {location.get_name()}")
    print(f"Description: {location.description}")
    if location.creatures:
        print("Creatures present:")
        for creature in location.creatures:
            print(f"- {creature.name}: {creature.description}")
    else:
        print("No creatures here.")

        # Checking to see if there are items in the current location
    if location.items:
        print("Items available in this location:")
        for item in location.items:
            print(f"- {item.name}: {item.description}")

def pick_item(self):
        # Picking item from the current location
    item_name=input("Which item would you like to pick? ")
    self.current_pymon.pick_item(item_name)

def view_inventory(self):
    print("Inventory: ", self.current_pymon.inventory)

def use_item(self):
    item_name=input("Which item would you like to use? ")
    self.current_pymon.use_item(item_name)
        
class Record:
    def __init__(self):
        self.locations=[]
        self.creatures=[]
        self.items=[]
        self.benched_pymons=[]
        

    def import_location(self, filename="locations.csv"):
        try:
            with open(filename, newline='') as csvfile:
                reader=csv.reader(csvfile)
                next(reader)
                for row in reader:
                    row=[i.strip() for i in row]
                    
                    name, description, w, n, e, s=row
                    location=Location(name, description, w, n, e, s)
                    
                    self.locations.append(location)
                    
            for i in self.locations:
                if i.doors['west']!='None' and not isinstance(i.doors['west'],Location):
                    i.connect_west(self.find_location(i.doors['west']))
                if i.doors['north']!='None' and not isinstance(i.doors['north'],Location):
                    i.connect_north(self.find_location(i.doors['north']))
                if i.doors['east']!='None' and not isinstance(i.doors['east'],Location):
                    i.connect_east(self.find_location(i.doors['east']))
                if i.doors['south']!='None' and not isinstance(i.doors['south'],Location):
                    i.connect_south(self.find_location(i.doors['south']))
        except FileNotFoundError:
            print("Locations file not found.")
    
    def get_locations(self):
        return self.locations
        
    def find_location(self,location_name):
        for i in self.locations :
            if i.name==location_name:
                return i

    def import_creatures(self, filename="creatures.csv"):
        try:
            with open(filename, newline='') as csvfile:
                reader=csv.reader(csvfile)
                next(reader)
                for row in reader:
                    # Checking if the creature is a pymon or not
                    nickname, description, adoptable= row
                    if adoptable.strip()=='no':
                        creature=Creature(nickname, description)
                    else:
                        creature=Pymon(nickname, description)
                    self.creatures.append(creature)
                    for i in self.locations:
                        if i.name=='Playground' and nickname=='Kitimon':
                            i.add_creature(creature)
                        elif i.name=='Beach' and nickname=='Sheep':
                            i.add_creature(creature)
                        elif i.name=='School' and nickname=='Marimon':
                            i.add_creature(creature)
        except FileNotFoundError:
            print("Creatures file not found.")

    def import_items(self, filename="items.csv"):
        try:
            with open(filename, newline='') as csvfile:
                reader=csv.reader(csvfile)
                next(reader)
                for row in reader:
                    row=[i.strip() for i in row]
                    nickname, description, pickable, consumable=row
                    item=Item(nickname, description, pickable, consumable)
                    self.items.append(item)
                    for i in self.locations:
                        if i.name=='Playground' and (nickname=='tree' or nickname=='potion'):
                            i.add_item(item)
                        elif i.name=='Beach' and nickname=='apple':
                            i.add_item(item)
                        elif i.name=='School' and nickname=='binocular':
                            i.add_item(item)
        except FileNotFoundError:
            print("Items file not found.")
    
class Operation:    
    
    def handle_menu(self):
        print("Please issue a command to your Pymon:")
        print("1) Inspect Pymon")
        print("2) Inspect current location")
        print("3) Move")
        print("4) Pick an Item")
        print("5) View Inventory")
        print("6) Challenge a creature")
        print("7) Exit the program")
        
    def inspect_pymon_menu(self):
        print("Inspect Pymon:")
        print("1) View current Pymon's details")
        print("2) List and select a benched Pymon to use")
        print("3) Return to main menu")

    def inspect_pymon(self):
        while True:
            self.inspect_pymon_menu()
            sub_choice=input("Choose an option: ")
        
            if sub_choice=="1":
            # Inspects current Pymon details
                self.current_pymon.inspect()
        
            elif sub_choice == "2":
            # List of benched Pymons
                if not self.record.benched_pymons:
                    print("No benched Pymons available.")
                    break
                else:
                    print("Benched Pymons:")
                    for i, pymon in enumerate(self.record.benched_pymons):
                        print(f"{i+1}) {pymon.name}: {pymon.description} (Energy: {pymon.energy})")

                pymon_choice=input("Enter the number of the Pymon to swap with current: ")
                try:
                    pymon_choice=int(pymon_choice) - 1
                    if 0<=pymon_choice<len(self.record.benched_pymons):
                        # Swaping Pymons
                        self.record.benched_pymons.append(self.current_pymon)
                        self.record.benched_pymons[pymon_choice].current_location=self.current_pymon.current_location
                        self.current_pymon = self.record.benched_pymons.pop(pymon_choice)
                    
                        print(f"Swapped to {self.current_pymon.name}.")
                    else:
                        print("Invalid choice.")
                except ValueError:
                    print("Please enter a valid number.")
            break
    
    def __init__(self):
        self.locations=[]
        self.current_pymon=Pymon("Kimimon","Starter Pymon")
        self.record=Record()  
    
    def setup(self):
        self.record.import_location()
        self.record.import_creatures()
        self.record.import_items()
        for location in self.record.get_locations():
            self.locations.append(location)

        # Spawining pymon in a random location
        a_random_number=generate_random_number(len(self.locations)-1)
        spawned_loc=self.locations[a_random_number]

        self.current_pymon.current_location=spawned_loc

    def display_setup(self):
        for location in self.locations:
            print(location.name + " has the following creatures:")
            for creature in location.creatures:
                print(f"-{creature.name}")
                

    
    def test_run(self):
        print(self.current_pymon.get_location().get_name())
        self.current_pymon.move("west")
        if self.current_pymon.get_location():
            print(self.current_pymon.get_location().get_name())
        
    def start_game(self):
        print("Welcome to Pymon World\n")
        print("It's just you and your loyal Pymon roaming around to find more Pymons to capture and adopt.\n")
        print("You started at ",self.current_pymon.get_location().get_name())

        while True:
            self.handle_menu()
            choice=input("Choose an option: ")

            if choice=="1":
                self.inspect_pymon()

            elif choice=="2":
                current_location=self.current_pymon.get_location()
                if current_location:
                    print(f"Location: {current_location.get_name()}")
                    print(f"Description: {current_location.description}")
                    if current_location.creatures:
                        print("Creatures present:")
                        for creature in current_location.creatures:
                            print(f"-{creature.name}: {creature.description}")
                    else:
                        print("No creatures here.")
    
                    if current_location and current_location.items:
                        print("Items available in this location:")
                        for item in current_location.items:
                            print(f"- {item.name}: {item.description}")
                    else:
                        print("No items available to pick up in this location.")

            elif choice=="3":
                direction=input("Enter direction (west, north, east, south): ").lower()
                self.current_pymon.move(direction)

            elif choice == "4":

                current_location = self.current_pymon.get_location()
                 # Checking to see if there are items in the current location
                if current_location and current_location.items:
                    print("Items available in this location:")
                    for item in current_location.items:
                        print(f"- {item.name}: {item.description}")

                    item_name=input("Enter the name of the item to pick: ")
                    self.current_pymon.pick_item(item_name)
                else:
                    print("No items available to pick up in this location.")

            elif choice=="5":
                self.current_pymon.view_inventory()

            elif choice=="6":
                # Getting the current location of the Pymon
                location=self.current_pymon.get_location()
                # Checking if there are creatures in this location
                if location and location.creatures:
                    print("Creatures here:")
                    for creature in location.creatures:
                        print(f"- {creature.name}")
                    # User has to choose a creature to battle
                    creature_name=input("Enter the name of the creature to challenge: ")
                    
                    # Finding the selected creature
                    found_creature=None
                    for creature in location.creatures:
                        print(f'{creature.name} : {creature.adoptable}')
                        if creature.name==creature_name and creature.adoptable=='yes':
                            found_creature=creature
                            break
                    # Starts the challenge or show error if creature not found
                    if found_creature is not None:
                        new_active_pymon=self.current_pymon.challenge(found_creature, self.record.benched_pymons, self.locations)
                        if new_active_pymon:
                            self.current_pymon=new_active_pymon
                    else:
                        print("No such creature here.")
                else:
                    print("No creatures to challenge.")

            elif choice=="7":
                print("Exiting game.")
                break
            else:
                print("Invalid option.")

if __name__=='__main__':
    ops=Operation()
    ops.setup()
    ops.display_setup()
    ops.start_game()