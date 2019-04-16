# Refactors

## Refactor 1 - [DRMutationIterator:parse]
### Rule 1
| Id | Line no. | Mutator                                                                              | Result   |
|:---|:---------|:-------------------------------------------------------------------------------------|:---------|
| 1  | 48       | negated conditional                                                                  | KILLED   |
| 2  | 49       | mutated return of Object value to if(x!=null) null else throw new RuntimeException() | KILLED   |
| 3  | 52       | negated conditional                                                                  | KILLED   |
| 4  | 53       | mutated return of Object value to if(x!=null) null else throw new RuntimeException() | KILLED   |
| 5  | 60       | Replaced integer addition with subtraction                                           | SURVIVED |
| 6  | 63       | Replaced integer addition with subtraction                                           | SURVIVED |
| 7  | 65       | mutated return of Object value to if(x!=null) null else throw new RuntimeException() | KILLED   |

**Original code**
```java
private DRMutation parse() throws IOException {
  String curLine = br.readLine();
  if (curLine == null) {
    return null;
  }
  /* Skip comments. */
  if (curLine.startsWith("##")) {
    return next();
  }

  int tab = curLine.indexOf('\t');
  int colon = curLine.indexOf(':');

  String gene = curLine.substring(0, tab);
  String drug = curLine.substring(tab + 1);

  String geneName = gene.substring(0, colon);
  String[] geneInfo = gene.substring(colon + 1).split(",");

  return new DRMutation(geneName, geneInfo[TYPE_IDX], geneInfo[CHANGE_IDX],
      geneInfo[FILTER_IDX], Integer.parseInt(geneInfo[POSITION_IDX]), drug);
}
```

**Refactor change**
```diff
- private DRMutation parse() throws IOException {
+ protected DRMutation parse() throws IOException {
  String curLine = br.readLine();
  if (curLine == null) {
```
Needed to make a direct test for the method. As the method is private, direct
tests were not possible. Therefore, it is changed to be protected.

**Constructor change**
```diff
- public DRMutationIterator(File file) throws IOException {
+ public DRMutationIterator(BufferedReader reader) {
-  super(new BufferedReader(new InputStreamReader(new FileInputStream(file), "UTF-8")));
+  super(reader);
   current = null;
   needParse = true;
}
```
Needed to make it possible to mock the reader object. Otherwise a direct link
to an existing file would be required.

**Test code**
```java
@Test
public void testParse() throws IOException, URISyntaxException {
  DRMutationIterator it = new DRMutationIterator((BufferedReader) null);

  // Mock the buffered reader to control the behavior of the reading.
  BufferedReader read = Mockito.mock(BufferedReader.class);
  it.br = read;

  Mockito.when(read.readLine()).thenReturn("geneName:typeOfMutation,change,filter,0	D");

  DRMutation expected = new DRMutation("geneName", "typeOfMutation", "change", "filter", 0, "D");
  DRMutation actual = it.parse();
  // No equals method was provided for DRMutation, ReflectionEquals used instead.
  Assert.assertThat(expected, new ReflectionEquals(actual));
}
```
By adding a direct test and the above mentioned refactors for the method `parse()`
and the constructor (to make the testing easier). The refactor for the constructor,
however, is not required but is only a matter of preference.

<!-- file: nl.tudelft.dnainator.parser.impl.DRMutationParserTest.java -->


## Refactor 2 - [method nl.tudelft.ph.branching.PullRequestAnalyzer:requestCommits]
### Rule 2
| Id | Line no. | Mutator                   | Result   |
|:---|:---------|:--------------------------|:---------|
| 1  | 202      | VoidMethodCallMutator     | KILLED   |
| 2  | 175      | NegateConditionalsMutator | KILLED   |
| 3  | 180      | VoidMethodCallMutator     | KILLED   |
| 4  | 182      | VoidMethodCallMutator     | KILLED   |
| 5  | 183      | VoidMethodCallMutator     | SURVIVED |

**Original code**
```java
  private void requestCommits(final PullRequest pullrequest, final ApiRequest apiRequest) {
    if (!MongoGet.getCommits(pullrequest, repoDesc)) {
      final Gson gson = new Gson();
      final String commitResponse = apiRequest.execute(pullrequest.getCommitUrl());
      // Fill the pull request with the commit information.
      pullrequest
          .setCommits(CommitParser.jsonToCommits(gson.fromJson(commitResponse, JsonArray.class)));
      // Get the commit statusses for all pull requests.
      requestCommitStatus(pullrequest, apiRequest);
      MongoSet.addCommits(pullrequest, repoDesc);
    }
  }
```

**After change**
```diff
  public boolean requestCommits(final PullRequest pullrequest, final ApiRequest apiRequest) {
    if (!MongoGet.getCommits(pullrequest, repoDesc)) {
      final Gson gson = new Gson();
      final String commitResponse = apiRequest.execute(pullrequest.getCommitUrl());
      // Fill the pull request with the commit information.
      boolean check1 = pullrequest
          .setCommits(CommitParser.jsonToCommits(gson.fromJson(commitResponse, JsonArray.class)));
      boolean check2 = requestCommitStatus(pullrequest, apiRequest);
      boolean check3 = MongoSet.addCommits(pullrequest, repoDesc);

      return check1 && check2 && check3;
    }
    return true;
  }
```

The called external functions should be changed to return booleans as well,
depending on the success of their action.

**Test code**
```java
  @Test
  public void testRequestCommitsSet() {
	  final PullRequest pullrequest = analyzer.getPullRequests().get(0);
	  // Check if all checks pass after requesting the commits for a pull request.
	  assertTrue(analyzer.requestCommits(pullrequest, apiRequest));
  }

```
<!-- file: nl.tudelft.dnainator.parser.impl.DRMutationParserTest.java -->

## Refactor 3 - [com.fasterxml.jackson.core.JsonGenerator:setSchema]
### Rule 4
| Id | Line no. | Mutator                   | Result      |
|:---|:---------|:--------------------------|:------------|
| 1  | 221      | NegateConditionalsMutator | NO_COVERAGE |

**Original code**
```java
public void setSchema(FormatSchema schema) {
        String schemaType = (schema == null) ? "NULL" : schema.getSchemaType();
        throw new UnsupportedOperationException("Generator of type "+getClass().getName()+" does not support schema of type '"
                +schemaType+"'");
    }
```

The result of the mutation tests tell us basically that this method is not covered
in any test. Therefore, to kill the generated mutant, a test should be added.
jackson-core uses JUnit 3 for this test suite. Therefore, exception asserting
has to be done in a try-catch clause.

  **Test code**

  ```java
  public void testSetSchema() throws Exception
  {
      OutputStream out = new ByteArrayOutputStream();
      JsonGenerator gen = JSON_F.createGenerator(ObjectWriteContext.empty(), out);

      try{
          gen.setSchema(null);
          fail();
      } catch (UnsupportedOperationException e) {
          assertEquals( "Generator of type com.fasterxml.jackson.core.json.UTF8JsonGenerator does not support " +
                  "schema of type 'NULL'", e.getMessage() );
      }
  }
  ```

## Refactor 4 - [org.jfree.data.time.ohlc.OHLCSeriesCollection:AddSeries]
### Rule 6
| Id | Line no. | Mutator                                                                           | Result   |
|:---|:---------|:----------------------------------------------------------------------------------|:---------|
| 1  | 116      | removed call to org/jfree/chart/util/Args::nullNotPermitted                       | SURVIVED |
| 2  | 118      | removed call to org/jfree/data/time/ohlc/OHLCSeries:addChangeListener             | SURVIVED |
| 3  | 119      | removed call to org/jfree/data/time/ohlc/OHLRCSeriesCollection:fireDatasetChanged | SURVIVED |

**Original code**
```java
public void addSeries(OHLCSeries series) {
    Args.nullNotPermitted(series, "series");
    this.data.add(series);
    series.addChangeListener(this);
    fireDatasetChanged();
}
```

**Refactor change**
```java
public boolean addSeries(OHLCSeries series) {         // boolean function
    Args.nullNotPermitted(series, "series");
    this.data.add(series);
    series.addChangeListener(this);
    return fireDatasetChanged();                      // return
}
```
addSeries is changed to become a boolean function. This allowes to check for
the fireDatasetChanged to be called successfully. This on its turn also checks
for the addChangeListener being added.

```diff
- protected void fireDatasetChanged() {
+ protected boolean fireDatasetChanged() {
    if (this.notify) {
        notifyListeners(new DatasetChangeEvent(this, this));
+       return true;
    }
+   return false;
}
```
The fireDatasetChanged also had to be changed to allow for the last return.
A withcoming benefit is that the fireDatasetChanged method, on its turn,
becomes easier to test. Here one can check if the if-statement is working
as intended.

**Test code**
```java
@Test(expected = IllegalArgumentException.class)
public void testAddSeriesArgsNull() {
    OHLCSeriesCollection c = new OHLCSeriesCollection();
    c.addSeries(null);
}
```
The first test is required to check for the first statement. An exception should
be thrown for the illegal null argument.

```java
@Test
public void testAddSeries() {
  OHLCSeriesCollection c = new OHLCSeriesCollection();
  OHLCSeries s = Mockito.mock(OHLCSeries.class);

  assertEquals(0, c.getSeriesCount()); // Verify empty.
  boolean returnValue = c.addSeries(s);
  assertEquals(1, c.getSeriesCount()); // Verify series added.
  assertTrue(returnValue);			// Check fireDatasetChanged was successful.

  Mockito.verify(s, Mockito.times(1)).addChangeListener(
      Mockito.any(OHLCSeriesCollection.class)); // Check if listener is added.
}
```
The above test checks for the series to be actually added, the fireDatasetChanged
to be successful and the addChangeListener for being called exactly once. This
kills all mutators for this function. Please note that for this change
Mockito was added as a dependency to the repository.

## Refactor 5 - [com.fasterxml.jackson.core.JsonGenerator:writeNumber]
### Rule 5
| Id | Line no. | Mutator               | Result      |
|:---|:---------|:----------------------|:------------|
| 1  | 895      | VoidMethodCallMutator | NO_COVERAGE |

**Original code**
```java
public void writeNumber(short v) throws IOException { writeNumber((int) v); }
```

The result of the mutation tests tell us basically that this method is not covered
in any test. Therefore, to kill the generated mutant, a test should be added.
The method 'writeNumber' is part of an abstract class though, so we have to test it
on an implementation of JsonGenerator. We noticed every implementation overwrites
'writeNumber' and therefore, this method is refactored to be abstract. This
also removed the mutant.

**Refactor change**
```java
public abstract void writeNumber(short v) throws IOException;
```

## Refactor 6 - [org.jfree.chart.ui.NumberCellRenderer:\<init\>]
### Rule 3
| Id | Line no. | Mutator               | Result      |
|:---|:---------|:----------------------|:------------|
| 1  | 48       | VoidMethodCallMutator | NO_COVERAGE |

**Original code**
```java
public NumberCellRenderer() {
    super();
    setHorizontalAlignment(SwingConstants.RIGHT);
}
```

The result of the mutation tests tell us basically that this method is not covered
in any test. Therefore, to kill the generated mutant, a test should be added.
This entire 'NumberCellRenderer' class is not tested, probably because it resides
in the UI package. When adding a test, the muting which removes the
'setHorizontalAlignment(SwingConstants.RIGHT);' statement is killed successfully.

**Added test code**
```java
@Test
public void testDrawWithNullInfo() {
    NumberCellRenderer numberCellRenderer = new NumberCellRenderer();
    assertEquals(SwingConstants.RIGHT, numberCellRenderer.getHorizontalAlignment());
}
```

## Refactor 7 - [nl.tudelft.dnainator.graph.impl.nodes.Neo4jSequenceNode:getScores]
### Rule 7
| Id | Line no. | Mutator                                                                                          | Result      |
|:---|:---------|:-------------------------------------------------------------------------------------------------|:------------|
| 1  | 134      | removed call to nl/tudelft/dnainator/graph/impl/nodes/Neo4jSequenceNode::load                    | NO_COVERAGE |
| 2  | 135      | mutated retorn of Object value for getScores to (if (x != null) null throw new RuntimeException) | NO_COVERAGE |

**Original Code**
```java
@Override
public Map<ScoreIdentifier, Integer> getScores() {
  load();
  return scores;
}
```
Important for this code is the call to `load()` (see below0).

```java
private void load() {
  if (loaded) {
    return;
  }

  try (Transaction tx = service.beginTx()) {
    start    = (int)    node.getProperty(SequenceProperties.STARTREF.name());
    end      = (int)    node.getProperty(SequenceProperties.ENDREF.name());
    sequence = (String) node.getProperty(SequenceProperties.SEQUENCE.name());
    rank     = (int)    node.getProperty(SequenceProperties.RANK.name());
    node.getRelationships(RelTypes.ANNOTATED, Direction.OUTGOING).forEach(e ->
        annotations.add(new Neo4jAnnotation(service, e.getEndNode())));
    for (ScoreIdentifier id : Scores.values()) {
      scores.put(id, (Integer) node.getProperty(id.name(), 0));
    }
    tx.success();
  }

  loaded = true;
}
```

**Refactor change:**
To make this method easier to test we can refactor the `void` to return the
`loaded` value. Furthermore, we can change the `private` to `protected` in
order to make it visible for direct tests. For these mutants, this is not
needed. However, it still makes is easier to tackle more mutants present in
this class.

```java
protected boolean load() {
  if (!loaded) {
    try (Transaction tx = service.beginTx()) {
      start    = (int)    node.getProperty(SequenceProperties.STARTREF.name());
      end      = (int)    node.getProperty(SequenceProperties.ENDREF.name());
      sequence = (String) node.getProperty(SequenceProperties.SEQUENCE.name());
      rank     = (int)    node.getProperty(SequenceProperties.RANK.name());
      node.getRelationships(RelTypes.ANNOTATED, Direction.OUTGOING).forEach(e ->
          annotations.add(new Neo4jAnnotation(service, e.getEndNode())));
      for (ScoreIdentifier id : Scores.values()) {
        scores.put(id, (Integer) node.getProperty(id.name(), 0));
      }
      tx.success();
    }
  }

  loaded = true;
  return loaded;
}
```

Because `loaded` is a global private variable, we need a getter for it in
order to allow the test method to check the `loaded` value.

```java
public boolean isLoaded() {
  return loaded;
}
```

Furthermore, we need to add new test methods for the function `getScores()`.

```java
@Test
public void testGetScores() {
  GraphDatabaseService service = mock(GraphDatabaseService.class);
  Node node = mock(Node.class);
  Transaction tx = mock(Transaction.class);

  // Mock the transaction steps for load.
  when(node.getProperty(Matchers.any())).thenReturn("").thenReturn(0).thenReturn(0).thenReturn(0).thenReturn("").thenReturn(0);
  when(node.getRelationships(Matchers.any(RelTypes.class), Matchers.any())).thenReturn(new ArrayList<>());
  when(service.beginTx()).thenReturn(tx);
  // Mock the return value of the scores properties.
  when(node.getProperty(Matchers.anyString(), Matchers.anyInt())).thenReturn(10);

  Neo4jSequenceNode nsn = new Neo4jSequenceNode(service, node);
  // Verify the sequence is not loaded.
  assertFalse(nsn.isLoaded());

  Map<ScoreIdentifier, Integer> result = nsn.getScores();
  Map<ScoreIdentifier, Integer> expected = new HashMap<>();
  expected.put(Scores.DR_MUT, 10);
  expected.put(Scores.SEQ_LENGTH, 10);

  // SequenceNode should now be loaded.
  assertTrue(nsn.isLoaded());
  // No results were gathered, as the transaction was cancelled.
  assertEquals(expected, result);
}
```

## Refactor 8 - [org.jfree.chart.axis.ValueAxis:setRangeWithMargins]
### Rule 8
| Id | Line no. | Mutator                                                             | Result      |
|:---|:---------|:--------------------------------------------------------------------|:------------|
| 1  | 1313     | Removed call to org/jfree/chart/axis/ValueAxis::setRangeWithMargins | NO_COVERAGE |
| 2  | 1331     | Removed call to org/jfree/chart/util/Args::nullNotPermitted         | NO_COVERAGE |
| 3  | 1332     | Removed call to org/jfree/chart/axis/ValueAxis:setRange             | NO_COVERAGE |
| 4  | 1345     | Removed call to org/jfree/chart/axis/ValueAxis:setRangeWithMargins  | NO_COVERAGE |


**Original Code:**
```java
public void setRangeWithMargins(Range range) {
    setRangeWithMargins(range, true, true);
}

public void setRangeWithMargins(Range range, boolean turnOffAutoRange,
                                boolean notify) {
    Args.nullNotPermitted(range, "range");
    setRange(Range.expand(range, getLowerMargin(), getUpperMargin()),
            turnOffAutoRange, notify);
}

public void setRangeWithMargins(double lower, double upper) {
    setRangeWithMargins(new Range(lower, upper));
}
```

**Refactor change:**
First of all, the methods appear to be highly observable and, therefore,
easy to tests. Thus, tests should be added.

```java
@Test
public void testSetRangeWithMargins() {
  ValueAxis axis = new NumberAxis();
  Range range = new Range(0, 10);
  axis.setRangeWithMargins(range); 	
  assertEquals(new Range(-0.5, 10.5), axis.getRange());
  axis.setRangeWithMargins(range, false, true);
  assertEquals(new Range(-0.5, 10.5), axis.getRange());
  axis.setRangeWithMargins(range, true, false);
  assertEquals(new Range(-0.5, 10.5), axis.getRange());
  axis.setRangeWithMargins(range, false, false);
  assertEquals(new Range(-0.5, 10.5), axis.getRange());
}

@Test(expected = IllegalArgumentException.class)
public void testSetRangeWithMarginsNull() {
  ValueAxis axis = new NumberAxis();
  axis.setRangeWithMargins(null);
}
```

The first test checks for all different arguments the right Range is created.
The second test checks if a null argument causes an IllegalArgumentException.
However, these two tests still are unable to kill the mutant on line 1331
`Removed call to org/jfree/chart/util/Args::nullNotPermitted`.

```diff
public void setRangeWithMargins(Range range, boolean turnOffAutoRange,
                                boolean notify) {
-    Args.nullNotPermitted(range, "range");
    setRange(Range.expand(range, getLowerMargin(), getUpperMargin()),
            turnOffAutoRange, notify);
}
```

With further inspection it becomes clear that is caused by the fact that the
check on line 1331 is unnecessary. In `Range.expand` this very same check is
done for the argument `range`. Therefore, this check in `setRangeWithMargins`
can be omitted.
