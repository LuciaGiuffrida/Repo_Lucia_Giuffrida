
array = [2,3,4,5,6,7,8,9,10]
somma=0
max_value= array[0]
min_value= array[0]

def minmax(array):
    
    global max_value,min_value
    for i in range(len(array)):
        if array[i] >= max_value:
            max_value = array[i]
        elif array[i] <= min_value:
            min_value =array[i]

    return (max_value, min_value) 

minmax(array)
print("Max", max_value, "Min", min_value)