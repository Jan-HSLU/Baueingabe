import ifcopenshell
import ifcopenshell.util.element 
import Helpers.Data_Helpers as hlp

def r6(model_paths):
    #Gesamtwohnungsanzahl
    all_flats = hlp.Wohnungsmix.get_gesamtzahl_aller_wohnungen()
    print("Rule 6: Es wurden insgesamt Anzahl Wohnungen ermittelt:")
    print(all_flats)

    return all_flats