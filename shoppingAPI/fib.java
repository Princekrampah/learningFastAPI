public class fib {
    public static void main(String args[]){
        // System.out.println(fibo(6));
        int[] arr = {40, 30, 40, 20, 30, 8};
        // System.out.println(meanAge(arr));

        int[] result = insertionSort(arr);

        for (int a: result){
            System.out.print(a + " ");
        }
    }

    public static int fibo(int num) {
        if (num == 0 || num == 1) {
            return num;
        }
        return fibo(num - 2) + fibo(num - 1);
    }

    public static double meanAge(int arr[]) {
        int sum = 0;
        for (int i = 0; i < arr.length; i++) {
            sum += arr[i];
        }
        return sum / arr.length;
    }

    public static int[] bubbleSort(int arr[]){
        for (int i = 0; i < arr.length; i++){
            for (int j = 0; j < arr.length - i - 1; j++){
                if (arr[j+1] < arr[j]){
                    int temp = arr[j+1];
                    arr[j+1] = arr[j];
                    arr[j] = temp;
                }
            }
        }
        return arr;
    }

    public static int[] insertionSort(int[] arr){
        for (int i = 1; i < arr.length; i++){
            int j = i - 1;
            int key = arr[i];
            while(j >= 0 && key < arr[j]){
                arr[j + 1] = arr[j];
                j--;
            }
            arr[j + 1] = key;
        }
        return arr;
    }
}