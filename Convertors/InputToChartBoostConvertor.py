from Enums.Enums import ChartBoostOrientations


class InputToChartBoostConvertor:
    @staticmethod
    def orientation(name):
        return ChartBoostOrientations[name].value
