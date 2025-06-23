import pandas as pd
import matplotlib.pyplot as plt

def prepare_data(df: pd.DataFrame, 
                drops: list = None, 
                inffo: bool = False,
                plot_pie: bool = False) -> pd.DataFrame:
    """
    Подготавливает DataFrame с возможностью визуализации распределения данных.
    
    Параметры:
        df: Исходный DataFrame
        drops: Список столбцов для удаления
        inffo: Флаг вывода подробной информации о столбцах
        plot_pie: Флаг построения круговых диаграмм для каждого столбца
    
    Возвращает:
        Обработанный DataFrame
    """
    if drops is None:
        drops = []

    # Поиск полностью пустых столбцов
    for col in df.columns:
        lenns = len(df[col])
        nans = df[col].isna().sum()
        
        if lenns == nans:
            drops.append(col)
        
        if inffo is True:
            print(f"\nСтолбец: {col}")
            print(df[col].value_counts(dropna=False))
            print(f'Всего: {lenns} | Полных: {lenns - nans} | Пустых: {nans}')
            print('-' * 50)

        # Построение pie-диаграмм
        if plot_pie and col not in drops:
            plt.figure(figsize=(8, 4))
            
            # Для числовых данных - гистограмма
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col].plot(kind='hist', title=f'Распределение {col}')
                plt.ylabel('Количество')
            
            # Для категориальных - pie chart
            else:
                value_counts = df[col].value_counts(dropna=False)
                if len(value_counts) > 10:
                    top10 = value_counts.head(10)
                    top10['Остальные'] = value_counts[10:].sum()
                    top10.plot(kind='pie', autopct='%1.1f%%', title=f'Top-10 значений {col}')
                else:
                    value_counts.plot(kind='pie', autopct='%1.1f%%', title=f'Распределение {col}')
            
            plt.tight_layout()
            plt.show()

    # Удаление указанных столбцов
    df = df.drop(columns=drops, errors='ignore')
    
    # Вывод информации
    print("\nОбщая информация о DataFrame:")
    print(df.info())
    
    if drops:
        print('-' * 100)
        print(f'Удаленные признаки: {drops}')

    return df


def save_prepared_data(df: pd.DataFrame, filename: str):
    """
    Сохраняет подготовленные данные в файл
    
    Параметры:
        df: Обработанный DataFrame
        filename: Имя файла для сохранения
    """
    df.to_csv(filename, index=False)
    print(f"Данные сохранены в файл: {filename}")


if __name__ == "__main__":
    print("Это модуль для подготовки данных")