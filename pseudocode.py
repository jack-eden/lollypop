def main():
    check for database
        if no path supplied ask for one
        if path supplied ensure it is a db file
            if not as for a db file (populate given string in input dialog) if the db file does not exist it will be created
        if db file does not already exists as the user if they would like to create one
            if creating a new database create a new sqlite db file with lollypop.db as the name, add the basic tables?
        once we have a db file check integrity
            create a new back-up following the given backup rotation scheme
            try to load the database and test for the basic table
        take an input directory to catalouge
            walk the directory, discarding hidden directories and files
            Generate my metadata for each file
                md5 sum, file loaction including unique drive identifier, full path, file name, file parent, regular filesystem metadata
            save metadata to db (use pools? Each pool can have as many drives added as you like and each one will be walked for files)
                list duplicate files
                list possible duplicates?
        generate a list of unique files across all drives using the fewest number of drives possibe
        copy files to a new location to create one complete set of all unique files on each drive
            

if __name__ == "__main__":
    main()