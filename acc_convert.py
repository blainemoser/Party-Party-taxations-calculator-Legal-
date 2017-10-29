def AccConv(in_number): #This function:-
                        #1 - converts numbers to strings;
                        #2 - separates numbers by commas;
                        #3 - truncates decimals to two places by rounding;
                        #4 - expresses numbers in the accounting convention.
    
    number = abs(in_number) #captures input as absolute value
    number = str(round(number, 2)) # rounds off the number to 2 decimals & converts the number to a string
    number_split = number.split(".") #splits the string into 2: the whole portion and decimal portion. This creates a list variable.

    whole_part = number_split[0]

    if len(number_split) == 2: #i.e. if it was NOT a whole number
        
        frac_part = number_split[1] #creates the fraction portion

    Len = len(whole_part) #the number of digits
    
    List = [int(Len/3),(Len%3)] # This is a 2 element list - first element (L[0]) is the integer value of the number of digits divided by 3;
                                # The second element (L[1]) is the remainder.

    if List[1] == 0: 

        commas = List[0] - 1 #If the number of digits perfectly divides by 3, then the number of commas is 1 less than the quotient.
        
    else:

        commas = List[0] # If there is a remainder, the number of commas equals the integer-qoutient
        
    comma_pos_list = [] #Creates a blank list into which comma positions will be stored.
    
    for i in range(1,(commas+1)): #Uses the number of commas to populate a list of appropriate size
        
        comma_pos_list.append(Len-(3*i)) #The comma position is given by the number of digits in the number (Len) less 3 times the number of commas

    for j in comma_pos_list:
        whole_part = whole_part[:j] + ',' + whole_part[j:] #moves through the list & adds commas at the correct position in the number.
    
    if len(number_split) < 2: #this conditional adds back the decimal numbers (or adds ".00" where the number is a whole-number)
        
        number = (whole_part+".00")
        
    elif len(frac_part) != 2: # If the original number contained a perfect 10th fraction, we add a zero for accounting purposes.
        
        number = (whole_part+"."+frac_part+"0")

    else:

        number = (whole_part+"."+frac_part)

    if in_number < 0: #negatives number if input was negative.

        number = ("("+number+")")

    else:
        pass
    
    return number



