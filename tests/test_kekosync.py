import unittest

from kekosync import KeKoSync


class TestGetWorkshopitemDependencies(unittest.TestCase):
    def test_illegal(self):
        self.assertRaises(ValueError, KeKoSync.get_workshopitem_dependencies, 'abcd')

    def test_nonexisting(self):
        KeKoSync.get_workshopitem_dependencies('1234')

    def test_empty(self):
        # CBA_A3, has no dependencies, https://steamcommunity.com/workshop/filedetails/?id=450814997
        self.assertEqual(KeKoSync.get_workshopitem_dependencies("450814997"), [])

    def test_single(self):
        # ace, has single dependency CBA_A3, https://steamcommunity.com/workshop/filedetails/?id=463939057
        self.assertEqual(KeKoSync.get_workshopitem_dependencies("463939057"), [{
            'name': 'CBA_A3',
            'url': 'https://steamcommunity.com/workshop/filedetails/?id=450814997',
            'workshopitem_id': '450814997'
        }])

    def test_multiple(self):
        # ACE Compats - RHS Compats has multiple deps, https://steamcommunity.com/sharedfiles/filedetails/?id=2216362075
        deps = KeKoSync.get_workshopitem_dependencies("2216362075")
        self.assertEqual(len(deps), 5)
        self.assertTrue({'name': 'ace', 'url': 'https://steamcommunity.com/workshop/filedetails/?id=463939057',
                         'workshopitem_id': '463939057'} in deps)
        self.assertTrue({'name': 'RHSAFRF', 'url': 'https://steamcommunity.com/workshop/filedetails/?id=843425103',
                         'workshopitem_id': '843425103'} in deps)
        self.assertTrue({'name': 'RHSGREF', 'url': 'https://steamcommunity.com/workshop/filedetails/?id=843593391',
                         'workshopitem_id': '843593391'} in deps)
        self.assertTrue({'name': 'RHSUSAF', 'url': 'https://steamcommunity.com/workshop/filedetails/?id=843577117',
                         'workshopitem_id': '843577117'} in deps)
        self.assertTrue({'name': 'RHSSAF', 'url': 'https://steamcommunity.com/workshop/filedetails/?id=843632231',
                         'workshopitem_id': '843632231'} in deps)


if __name__ == '__main__':
    unittest.main()
