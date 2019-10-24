import ast

EXAMPLE_CLIPBOARD_PASTE = """['keko_faction_generic_blufor_sql',[["arifle_Katiba_ARCO_pointer_F","","acc_pointer_IR","optic_Arco_blk_F",["30Rnd_65x39_caseless_green",30],[],""],[],["hgun_Rook40_F","","","",["16Rnd_9x21_Mag",17],[],""],["U_O_CombatUniform_ocamo",[["FirstAidKit",1],["30Rnd_65x39_caseless_green",2,30]]],["V_TacVest_khk",[["30Rnd_65x39_caseless_green",1,30],["30Rnd_65x39_caseless_green_mag_Tracer",2,30],["16Rnd_9x21_Mag",2,17],["HandGrenade",2,1],["O_IR_Grenade",2,1],["SmokeShell",1,1],["SmokeShellRed",1,1],["SmokeShellOrange",1,1],["SmokeShellYellow",1,1],["Chemlight_red",2,1]]],[],"H_HelmetLeaderO_ocamo","",["Binocular","","","",[],[],""],["ItemMap","ItemGPS","ItemRadio","ItemCompass","ItemWatch","NVGoggles_OPFOR"]]]
['keko_faction_generic_blufor_medic',[["arifle_Katiba_pointer_F","","acc_pointer_IR","",["30Rnd_65x39_caseless_green",30],[],""],[],["hgun_Rook40_F","","","",["16Rnd_9x21_Mag",17],[],""],["U_O_CombatUniform_ocamo",[["FirstAidKit",1],["30Rnd_65x39_caseless_green",2,30]]],["V_TacVest_khk",[["30Rnd_65x39_caseless_green",3,30],["16Rnd_9x21_Mag",2,17],["SmokeShell",1,1],["SmokeShellRed",1,1],["SmokeShellOrange",1,1],["SmokeShellYellow",1,1],["Chemlight_red",2,1]]],["B_FieldPack_ocamo_Medic",[["Medikit",1],["FirstAidKit",10]]],"H_HelmetO_ocamo","",[],["ItemMap","","ItemRadio","ItemCompass","ItemWatch","NVGoggles_OPFOR"]]]
['keko_faction_generic_blufor_ftl',[["srifle_DMR_01_DMS_BI_F","","","optic_DMS",["10Rnd_762x54_Mag",10],[],"bipod_02_F_blk"],[],["hgun_Rook40_F","","","",["16Rnd_9x21_Mag",17],[],""],["U_O_CombatUniform_ocamo",[["FirstAidKit",1],["10Rnd_762x54_Mag",3,10],["SmokeShell",1,1]]],["V_TacVest_khk",[["10Rnd_762x54_Mag",6,10],["16Rnd_9x21_Mag",2,17],["HandGrenade",2,1],["SmokeShellRed",1,1],["Chemlight_red",2,1]]],[],"H_HelmetO_ocamo","",[],["ItemMap","","ItemRadio","ItemCompass","ItemWatch","NVGoggles_OPFOR"]]]
['keko_faction_generic_blufor_grenadier',[["arifle_Katiba_ACO_pointer_F","","acc_pointer_IR","optic_ACO_grn",["30Rnd_65x39_caseless_green",30],[],""],[],["hgun_Rook40_F","","","",["16Rnd_9x21_Mag",17],[],""],["U_O_CombatUniform_ocamo",[["FirstAidKit",1],["30Rnd_65x39_caseless_green",2,30]]],["V_HarnessO_brn",[["30Rnd_65x39_caseless_green",9,30],["16Rnd_9x21_Mag",2,17],["HandGrenade",2,1],["SmokeShell",1,1],["SmokeShellRed",1,1],["Chemlight_red",2,1]]],["B_FieldPack_cbr_Ammo",[["FirstAidKit",4],["30Rnd_65x39_caseless_green",6,30],["150Rnd_762x54_Box",1,150],["RPG32_F",1,1],["HandGrenade",2,1],["MiniGrenade",2,1],["1Rnd_HE_Grenade_shell",6,1],["10Rnd_93x64_DMR_05_Mag",2,10],["10Rnd_762x51_Mag",3,10]]],"H_HelmetO_ocamo","",[],["ItemMap","","ItemRadio","ItemCompass","ItemWatch","NVGoggles_OPFOR"]]]
['keko_faction_generic_blufor_lmg',[["arifle_Katiba_ACO_F","","","optic_ACO_grn",["30Rnd_65x39_caseless_green",30],[],""],["launch_RPG32_F","","","",["RPG32_F",1],[],""],["hgun_Rook40_F","","","",["16Rnd_9x21_Mag",17],[],""],["U_O_CombatUniform_ocamo",[["FirstAidKit",1],["30Rnd_65x39_caseless_green",2,30]]],["V_TacVest_khk",[["30Rnd_65x39_caseless_green",3,30],["16Rnd_9x21_Mag",2,17],["SmokeShell",1,1],["SmokeShellRed",1,1],["Chemlight_red",2,1]]],["B_FieldPack_cbr_LAT",[["RPG32_F",2,1],["RPG32_HE_F",2,1]]],"H_HelmetO_ocamo","",[],["ItemMap","","ItemRadio","ItemCompass","ItemWatch","NVGoggles_OPFOR"]]]
['keko_faction_generic_blufor_rifleman_at',[["LMG_Zafir_pointer_F","","acc_pointer_IR","",["150Rnd_762x54_Box",150],[],""],[],["hgun_Rook40_F","","","",["16Rnd_9x21_Mag",17],[],""],["U_O_CombatUniform_ocamo",[["FirstAidKit",1],["16Rnd_9x21_Mag",2,17],["HandGrenade",1,1],["SmokeShell",1,1],["SmokeShellRed",1,1]]],["V_HarnessO_brn",[["150Rnd_762x54_Box",3,150],["Chemlight_red",2,1]]],[],"H_HelmetO_ocamo","",[],["ItemMap","","ItemRadio","ItemCompass","ItemWatch","NVGoggles_OPFOR"]]]
['keko_faction_generic_blufor_ftl',[["arifle_Katiba_ACO_pointer_F","","acc_pointer_IR","optic_ACO_grn",["30Rnd_65x39_caseless_green",30],[],""],[],["hgun_Rook40_F","","","",["16Rnd_9x21_Mag",17],[],""],["U_O_CombatUniform_ocamo",[["FirstAidKit",1],["30Rnd_65x39_caseless_green",2,30]]],["V_HarnessO_brn",[["30Rnd_65x39_caseless_green",7,30],["16Rnd_9x21_Mag",2,17],["HandGrenade",2,1],["SmokeShell",1,1],["SmokeShellRed",1,1],["Chemlight_red",2,1]]],[],"H_HelmetO_ocamo","",[],["ItemMap","","ItemRadio","ItemCompass","ItemWatch","NVGoggles_OPFOR"]]]
['keko_faction_generic_blufor_grenadier',[["arifle_Katiba_ACO_pointer_F","","acc_pointer_IR","optic_ACO_grn",["30Rnd_65x39_caseless_green",30],[],""],[],["hgun_Rook40_F","","","",["16Rnd_9x21_Mag",17],[],""],["U_O_CombatUniform_ocamo",[["FirstAidKit",1],["30Rnd_65x39_caseless_green",2,30]]],["V_HarnessO_brn",[["30Rnd_65x39_caseless_green",9,30],["16Rnd_9x21_Mag",2,17],["HandGrenade",2,1],["SmokeShell",1,1],["SmokeShellRed",1,1],["Chemlight_red",2,1]]],["B_FieldPack_cbr_Ammo",[["FirstAidKit",4],["30Rnd_65x39_caseless_green",6,30],["150Rnd_762x54_Box",1,150],["RPG32_F",1,1],["HandGrenade",2,1],["MiniGrenade",2,1],["1Rnd_HE_Grenade_shell",6,1],["10Rnd_93x64_DMR_05_Mag",2,10],["10Rnd_762x51_Mag",3,10]]],"H_HelmetO_ocamo","",[],["ItemMap","","ItemRadio","ItemCompass","ItemWatch","NVGoggles_OPFOR"]]]
['keko_faction_generic_blufor_lmg',[["arifle_Katiba_GL_ARCO_pointer_F","","acc_pointer_IR","optic_Arco_blk_F",["30Rnd_65x39_caseless_green",30],["1Rnd_HE_Grenade_shell",1],""],[],["hgun_Rook40_F","","","",["16Rnd_9x21_Mag",17],[],""],["U_O_CombatUniform_ocamo",[["FirstAidKit",1],["30Rnd_65x39_caseless_green",2,30]]],["V_HarnessOGL_brn",[["30Rnd_65x39_caseless_green",1,30],["30Rnd_65x39_caseless_green_mag_Tracer",2,30],["16Rnd_9x21_Mag",2,17],["MiniGrenade",2,1],["1Rnd_HE_Grenade_shell",5,1],["SmokeShell",1,1],["SmokeShellRed",1,1],["SmokeShellOrange",1,1],["SmokeShellYellow",1,1],["Chemlight_red",2,1],["1Rnd_Smoke_Grenade_shell",2,1],["1Rnd_SmokeRed_Grenade_shell",1,1],["1Rnd_SmokeOrange_Grenade_shell",1,1],["1Rnd_SmokeYellow_Grenade_shell",1,1]]],[],"H_HelmetLeaderO_ocamo","",["Binocular","","","",[],[],""],["ItemMap","ItemGPS","ItemRadio","ItemCompass","ItemWatch","NVGoggles_OPFOR"]]]
['keko_faction_generic_blufor_rifleman_at',,[["arifle_Katiba_ACO_F","","","optic_ACO_grn",["30Rnd_65x39_caseless_green",30],[],""],["launch_RPG32_F","","","",["RPG32_F",1],[],""],["hgun_Rook40_F","","","",["16Rnd_9x21_Mag",17],[],""],["U_O_CombatUniform_ocamo",[["FirstAidKit",1],["30Rnd_65x39_caseless_green",2,30]]],["V_TacVest_khk",[["30Rnd_65x39_caseless_green",3,30],["16Rnd_9x21_Mag",2,17],["SmokeShell",1,1],["SmokeShellRed",1,1],["Chemlight_red",2,1]]],["B_FieldPack_cbr_LAT",[["RPG32_F",2,1],["RPG32_HE_F",2,1]]],"H_HelmetO_ocamo","",[],["ItemMap","","ItemRadio","ItemCompass","ItemWatch","NVGoggles_OPFOR"]]]"""

EXAMPLE_CLIPBOARD_PASTE_SINGLE = """# Faction Generator Config Export
['keko_faction_generic_blufor_rifleman',[["rhs_weap_m4_m203S","ACE_muzzle_mzls_L","rhs_acc_2dpZenit_ris","rhsusf_acc_ACOG_USMC",["rhs_mag_30Rnd_556x45_M855A1_Stanag",30],["1Rnd_HE_Grenade_shell",1],""],["rhs_weap_smaw_gr_optic","","acc_pointer_IR","rhs_weap_optic_smaw",["rhs_mag_smaw_HEDP",1],["rhs_mag_smaw_SR",5],""],["hgun_Pistol_heavy_01_F","muzzle_snds_acp","acc_flashlight_pistol","optic_MRD",["11Rnd_45ACP_Mag",11],[],""],["rhs_uniform_FROG01_d",[["FirstAidKit",1],["rhsusf_ANPVS_14",1]]],["rhsusf_spc_light",[["rhs_mag_m67",1,1]]],["rhsusf_assault_eagleaiii_coy_assaultman",[["rhs_mag_smaw_HEDP",1,1],["rhsusf_m112_mag",1,1]]],"rhsusf_lwh_helmet_marpatd","rhs_googles_black",["Rangefinder","","","",[],[],""],["ItemMap","ItemGPS","TFAR_anprc152","ItemCompass","ItemWatch","NVGoggles_OPFOR"]]]"""


def _strip_classname(classname):
    for side_str in ["blufor", "indfor", "opfor"]:
        prefix = "keko_faction_generic_{}_".format(side_str)
        if classname.startswith(prefix):
            return classname[len(prefix):]


def generate_config(clipboard_paste):
    all = []
    for line in clipboard_paste.splitlines():
        if line.startswith('#'):
            continue
        print(line)

        unit = dict()
        unit['class'], loadout = ast.literal_eval(line)
        unit['primary_weapon'], unit['secondary_weapon'], unit['handgun'], unit['uniform'], unit['vest'], unit[
            'backpack'], unit['helmet'], unit['goggles'], unit['binocular'], unit['assigned_items'] = loadout

        print(unit)

    return all


if __name__ == "__main__":
    generate_config(EXAMPLE_CLIPBOARD_PASTE_SINGLE)
