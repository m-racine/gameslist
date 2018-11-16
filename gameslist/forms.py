#https://stackoverflow.com/questions/38965677/django-how-to-show-and-hide-div-based-on-the-selection-of-the-dropdown-menu
#Forms.py

BLANK_CHOICE = (('', '----------'),)
PALLET = 'Pallet'
RACK = 'Rack'
BOX = 'Box'

PACK_TYPE = (
    (PALLET, 'Pallet'),
    (RACK, 'Rack'),
    (BOX, 'Box'),
)

item_packmethod = forms.ChoiceField(label="Pack Method", choices = BLANK_CHOICE + PACK_TYPE,required=False)