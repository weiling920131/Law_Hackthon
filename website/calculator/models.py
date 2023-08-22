from django.db import models

cols = [
    '縣市', '鄉鎮市區', '地址地號', '交易日期', '總價元', '單價元坪', '總面積坪', '交易標的', '建物型態', '建築完成年', '房', '廳', '衛', '車位類別'
]
    
class dist(models.Model):
    dist_id = models.CharField(max_length=1)
    name = models.CharField(max_length=10)
    def __str__(self):
        return self.name

class township(models.Model):
    dist_id = models.CharField(max_length=1)
    name = models.CharField(max_length=10)
    def __str__(self):
        return self.name
