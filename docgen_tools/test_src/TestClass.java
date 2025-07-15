public class TestClass {
    private String name;
    private int value;
    
    public TestClass(String name, int value) {
        this.name = name;
        this.value = value;
    }
    
    public String getName() {
        return name;
    }
    
    public int getValue() {
        return value;
    }
    
    public void processData() {
        System.out.println("Processing: " + name + " with value " + value);
    }
}
