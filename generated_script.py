def generate_java_table_code(num_tables, max_range):
    """Generates Java code to print multiplication tables."""

    java_code = """
import java.util.Scanner;

public class MultiplicationTables {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.println("Enter the number of tables you want to generate:");
        int numTables = scanner.nextInt();

        System.out.println("Enter the range for each table:");
        int range = scanner.nextInt();

        for (int i = 1; i <= numTables; i++) {
            System.out.println("\\nMultiplication Table for " + i + ":");
            for (int j = 1; j <= range; j++) {
                System.out.println(i + " x " + j + " = " + (i * j));
            }
        }
        scanner.close();
    }
}
"""

    #Replace placeholders with user input if you want to hardcode values into generated Java
    #java_code = java_code.replace("numTables", str(num_tables))
    #java_code = java_code.replace("range", str(max_range))


    return java_code


#Get user input (optional - if you want to hardcode, comment this out)
num_tables = int(input("Enter the number of tables: "))
max_range = int(input("Enter the range for each table: "))


java_code = generate_java_table_code(num_tables, max_range)

# Write the Java code to a file
with open("MultiplicationTables.java", "w") as f:
    f.write(java_code)

print("Java code generated successfully.  Save the file as MultiplicationTables.java and compile and run it using a Java compiler (like javac).")