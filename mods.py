
def mod_gamemodes():
    from glob import iglob
    import os
    import importlib
    gamemodes = {}
    for mod_directory in iglob("mods\\*"):
        name = os.path.basename(mod_directory)

        if not os.path.exists(f"{mod_directory}\\mod.py"):
            continue

        module_path = os.path.abspath(f"{mod_directory}\\mod.py")
        spec = importlib.util.spec_from_file_location("mod", module_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if not hasattr(mod, "GAMEMODES"):
            continue
        for value in mod.GAMEMODES.values():
            if not isinstance(value, Gamemode):
                break
        else: # kein break fand statt
            gamemodes.update(mod.GAMEMODES)
    return gamemodes
