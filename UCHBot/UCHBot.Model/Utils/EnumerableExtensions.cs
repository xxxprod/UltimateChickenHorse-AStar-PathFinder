namespace UCHBot.Model.Utils;

public static class EnumerableExtensions
{
    [DebuggerStepThrough]
    public static int IndexOf<T>(this IEnumerable<T> enumerable, Func<T, bool> func)
    {
        int index = 0;
        foreach (T item in enumerable)
        {
            if (func(item))
                return index;
            index++;
        }

        return -1;
    }

    [DebuggerStepThrough]
    public static IEnumerable<T> WhereNot<T>(this IEnumerable<T> enumerable, Func<T, bool> func)
    {
        return enumerable.Where(a => !func(a));
    }
    
    [DebuggerStepThrough]
    public static IEnumerable<(int i, T Item)> WithIndex<T>(this IEnumerable<T> enumerable)
    {
        return enumerable.Select((x, i) => (i, x));
    }
    
    //[DebuggerStepThrough]
    //public static IEnumerable<(T item, TValue sum)> CumSum<T, TValue>(this IEnumerable<T> enumerable, Func<T, TValue> getter)
    //where TValue : INumber<TValue>
    //{
    //    TValue sum = default(TValue);
    //    foreach (T item in enumerable)
    //        yield return (item, sum += getter(item));
    //}

    
    public static IEnumerable<(TFirst First, TSecond Second)> ZipExact<TFirst, TSecond>(this IEnumerable<TFirst> first, IEnumerable<TSecond> second)
    {
        using IEnumerator<TFirst> e1 = first.GetEnumerator();
        using IEnumerator<TSecond> e2 = second.GetEnumerator();


        while (true)
        {
            bool e1Next = e1.MoveNext();
            bool e2Next = e2.MoveNext();
            
            if(e1Next ^ e2Next)
                throw new Exception("Data length mismatch");

            if (!e1Next)
                yield break;

            yield return (e1.Current, e2.Current);
        }
    }
}