from rest_framework import serializers


class PeriodSerializer(serializers.Serializer):
    """Serializer for date period information."""

    start = serializers.DateField()
    end = serializers.DateField()


class SummarySerializer(serializers.Serializer):
    """Serializer for financial summary."""

    period = PeriodSerializer()
    total_income = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=15, decimal_places=2)
    net = serializers.DecimalField(max_digits=15, decimal_places=2)
    transaction_count = serializers.IntegerField()


class CategoryBreakdownSerializer(serializers.Serializer):
    """Serializer for category-level breakdown."""

    category_id = serializers.UUIDField()
    category = serializers.CharField()
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    percentage = serializers.FloatField()
    count = serializers.IntegerField()


class DailyTrendSerializer(serializers.Serializer):
    """Serializer for daily trend data."""

    date = serializers.DateField()
    income = serializers.DecimalField(max_digits=15, decimal_places=2)
    expenses = serializers.DecimalField(max_digits=15, decimal_places=2)
    net = serializers.DecimalField(max_digits=15, decimal_places=2)


class BudgetStatusItemSerializer(serializers.Serializer):
    """Serializer for budget status in reports."""

    budget_id = serializers.UUIDField()
    category = serializers.CharField()
    allocated = serializers.FloatField()
    spent = serializers.FloatField()
    remaining = serializers.FloatField()
    percentage_used = serializers.FloatField()


class ReportSummarySerializer(serializers.Serializer):
    """Serializer for financial summary report."""

    period = PeriodSerializer()
    summary = SummarySerializer()
    by_category = CategoryBreakdownSerializer(many=True)


class TrendsReportSerializer(serializers.Serializer):
    """Serializer for trends report."""

    period = PeriodSerializer()
    trends = DailyTrendSerializer(many=True)


class MonthlyReportSerializer(serializers.Serializer):
    """Serializer for monthly detailed report."""

    year = serializers.IntegerField()
    month = serializers.IntegerField()
    summary = SummarySerializer()
    by_category = CategoryBreakdownSerializer(many=True)
    daily_trends = DailyTrendSerializer(many=True)
    budget_status = BudgetStatusItemSerializer(many=True)


class ComparisonReportSerializer(serializers.Serializer):
    """Serializer for period comparison report."""

    period_1 = SummarySerializer()
    period_2 = SummarySerializer()
    changes = serializers.DictField()
