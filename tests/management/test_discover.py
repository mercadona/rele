from rele.management.discover import discover_subs_modules


class TestDiscoverSubsModules:
    def test_returns_settings_and_paths_when_settings_found(self):
        paths = discover_subs_modules()
        # habrá que crear las carpetas y luego eliminarlas ya que las subs de test no sirve porque test no es una app y por eso seguramente no tenía tests
        assert paths == ["rele.subs", "rele.more_subs.subs"]
