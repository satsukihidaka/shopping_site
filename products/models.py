from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name="カテゴリ名")
    slug = models.SlugField(max_length=50, unique=True, help_text="URL用の文字列（例: tops）")

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products', verbose_name="カテゴリ")
    title = models.CharField(max_length=100, verbose_name="商品名")
    description = models.TextField(verbose_name="商品説明")
    price = models.IntegerField(verbose_name="価格")
    
    # 🚨 ここです！この行が「完全に」入っているか確認してください
    image = models.ImageField(upload_to='products/', verbose_name="メイン画像", blank=True, null=True)
    
    is_available = models.BooleanField(default=True, verbose_name="販売中か（在庫あり）")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="登録日時")

    def __str__(self):
        return self.title